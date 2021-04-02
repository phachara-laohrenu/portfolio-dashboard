from resources.retriever import Retriever

class Analyser:
    def __init__(self, asset_list):
        self.asset_list  = asset_list
        retriever = Retriever()
        self.time_series_df = retriever.combine_timeseries(self.asset_list)
    
    def analyse(self):
        self.time_series_df = self.fill_missing(self.time_series_df)
        self.time_series_df = self.calculate_return(self.time_series_df)
        correlation = self.time_series_df.corr()
        return correlation
        

    def fill_missing(self, time_series_df):
        return time_series_df.ffill()
    
    def calculate_return(self,time_series_df):
        time_series_df = (time_series_df - time_series_df.shift(1))/time_series_df.shift(1)
        return time_series_df