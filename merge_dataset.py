import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import List
from pathlib import Path

class BikeDataProcessor:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.numerical_cols = ['temp', 'atemp', 'hum', 'windspeed', 'casual', 'registered', 'cnt']

    def load_data(self) -> tuple:
        """Load hourly and daily data from CSV files, handling ParserError."""
        file_paths = {
            'hourly': self.data_dir / 'hour.csv',
            'daily': self.data_dir / 'day.csv'
        }

        for path in file_paths.values():
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

        try:
            hourly_data = self._preprocess_raw_data(pd.read_csv(file_paths['hourly']))
            daily_data = self._preprocess_raw_data(pd.read_csv(file_paths['daily']))
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file: {e}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred when loading or preprocessing: {e}")

        return hourly_data, daily_data

    def _preprocess_raw_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Initial preprocessing of raw data."""
        df['dteday'] = pd.to_datetime(df['dteday'])
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers using Winsorization."""
        df_cleaned = df.copy()
        for col in self.numerical_cols:
            if col in df_cleaned.columns:
                lower_limit = df_cleaned[col].quantile(0.01)
                upper_limit = df_cleaned[col].quantile(0.99)
                df_cleaned[col] = df_cleaned[col].clip(lower=lower_limit, upper=upper_limit)
        return df_cleaned

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add new features to the dataset."""
        df['day_name'] = df['dteday'].dt.day_name()
        df['year_month'] = df['dteday'].dt.to_period('M').astype(str)
        return df

    def aggregate_hourly_to_daily(self, hourly_data: pd.DataFrame) -> pd.DataFrame:
        """Aggregate hourly data to daily level."""
        agg_dict = {
            'season': 'first',
            'yr': 'first',
            'mnth': 'first',
            'hr' : 'first',
            'holiday': 'first',
            'weekday': 'first',
            'workingday': 'first',
            'weathersit': 'first',
            'temp': 'mean',
            'atemp': 'mean',
            'hum': 'mean',
            'windspeed': 'mean',
            'casual': 'mean',
            'registered': 'mean',
            'cnt': 'mean',
            'day_name': 'first',
            'year_month': 'first'
        }

        daily_data = (hourly_data.groupby('dteday')
                      .agg(agg_dict)
                      .reset_index())
        return daily_data

    def merge_with_daily(self, hourly_aggregated: pd.DataFrame, daily_data: pd.DataFrame) -> pd.DataFrame:
        """Merge aggregated hourly data with daily data."""
        daily_data_renamed = daily_data.rename(
            columns={col: 'daily_' + col for col in daily_data.columns if col in hourly_aggregated.columns and col != 'dteday'}
        )
        merged_data = pd.merge(hourly_aggregated, daily_data_renamed, on='dteday', how='left')

        if 'daily_instant' in merged_data.columns:
          merged_data.rename(columns={'daily_instant' : 'instant'}, inplace=True)
        return merged_data

    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize numerical columns using MinMaxScaler."""
        df_normalized = df.copy()
        missing_cols = set(self.numerical_cols) - set(df_normalized.columns)
        if missing_cols:
            print(f"Warning: Columns {missing_cols} are not present in the DataFrame. Normalization will not be applied to these columns.")

        for col in self.numerical_cols:
            if col in df_normalized.columns:
                scaler = MinMaxScaler()
                df_normalized[col] = scaler.fit_transform(df_normalized[[col]])
        return df_normalized

    def save_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to CSV."""
        dashboards_dir = self.data_dir.parent / 'dashboards'
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = dashboards_dir / filename
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path} (full path: {output_path.resolve()})")

def main():
    data_dir = Path('data')
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir.resolve()}")
        return

    processor = BikeDataProcessor(data_dir)

    try:
        hourly_data, daily_data = processor.load_data()

        hourly_featured = processor.add_features(hourly_data)
        hourly_aggregated = processor.aggregate_hourly_to_daily(hourly_featured)
        hourly_cleaned = processor.clean_data(hourly_aggregated)

        daily_data_cleaned = processor.clean_data(daily_data)
        merged_data = processor.merge_with_daily(hourly_cleaned, daily_data_cleaned)
        merged_normalized = processor.normalize_data(merged_data)
        
        print(f"Saving merged dataset to 'dashboards' folder alongside data directory")
        processor.save_data(merged_normalized, 'merged_dataset.csv')

        print("\nMerged Daily Data (First 5 rows):")
        print(merged_normalized.head())
        print("\nData Types of Merged Daily Data:")
        print(merged_normalized.dtypes)

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
