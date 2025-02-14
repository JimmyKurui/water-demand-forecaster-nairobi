import os
import torch
from torch import nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import PowerTransformer

from flask import current_app

model_path = os.path.join(current_app.root_path, 'data/models/lstm_water_forecast.pth')
data_path = os.path.join(current_app.root_path, 'data/files/normalized_data.csv')

class WaterUsageLSTM(nn.Module):
    def __init__(self, input_size=2, hidden_size=64, num_layers=2, output_size=1, dropout=0.2):
        super(WaterUsageLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_time_step = lstm_out[:, -1, :]  
        return self.fc(last_time_step)
    
class MIL():
    def __init__(self):
        INPUT_SIZE = 4 
        HIDDEN_SIZE = 64
        NUM_LAYERS = 2
        OUTPUT_SIZE = 4
        DROPOUT = 0.2
        device = 'cuda:01' if torch.cuda.is_available() else 'cpu'
        model = WaterUsageLSTM(INPUT_SIZE, HIDDEN_SIZE, NUM_LAYERS, OUTPUT_SIZE, DROPOUT)
        model.to(device)
        model.load_state_dict(torch.load(model_path, weights_only=True))
        self.model = model.eval()

    def predict(self, location, month):
        log = PowerTransformer()
        water_df = pd.read_csv(data_path, index_col='date', parse_dates=['date'])
        df = log.fit_transform(water_df.to_numpy())
        start_points = torch.tensor(df[-10:], dtype=torch.float32).unsqueeze(0)
        start_month = water_df.tail(1).index[0]
        
        while start_month <= month:
            with torch.no_grad():
                y_hat = self.model(start_points)
            start_points = torch.roll(start_points, shifts=-1, dims=2)
            start_points = torch.cat((start_points, y_hat.unsqueeze(0)), dim=1)
            new_month = start_month + pd.DateOffset(months=1)
            water_df.loc[new_month] = log.inverse_transform(y_hat.numpy())[0]
            start_month = new_month

        y_hat = log.inverse_transform(y_hat.numpy())
        return y_hat[0], water_df