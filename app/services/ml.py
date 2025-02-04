# Machine Learning Model
#  - It no, month, year, R tag, pop, volume, water_pp, percapita
#  - tariff per house type, tariff per pipe/ transport e.g. pipe, tank
#  - cost structure NW, delivery targets, investments

# R1 - 
# R2 - 
# R3 - 
# R4 - 

import os
import torch
from torch import nn
import numpy as np
from sklearn.preprocessing import PowerTransformer

from flask import current_app
from ..constants import R1, R2, R3, R4

model_path = os.path.join(current_app.root_path, 'models/lstm_water_forecast.pth')

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
        # device = 'cuda:01' if torch.cuda.is_available() else 'cpu'
        model = WaterUsageLSTM(INPUT_SIZE, HIDDEN_SIZE, NUM_LAYERS, OUTPUT_SIZE, DROPOUT)
        # model.to(device)
        model.load_state_dict(torch.load(model_path, weights_only=True))
        self.model = model.eval()
    
    def predict(self, location, household_volume, month):
        X = [
            (household_volume * 1.5) if location in R1 else 0.0,
            (household_volume * 1.0) if location in R2 else 0.0,
            (household_volume * 1.5) if location in R3 else 0.0,
            (household_volume * 1.5) if location in R4 else 0.0,
        ]
        X = torch.tensor(np.array([X])).float()
        log = PowerTransformer()
        df = log.fit_transform(X)
        x_test = torch.tensor([df]).float()
        y_hat = self.model(x_test)
        print(y_hat)
        y_hat = log.inverse_transform(y_hat.detach().numpy())
        return y_hat.tolist()[0]