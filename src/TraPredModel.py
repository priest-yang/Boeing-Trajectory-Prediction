import torch
import torch.nn as nn
from torch.autograd import Variable 


class TraPredModel(nn.Module):
    def __init__(self, input_size = None, lookback = None,  layers :list =[256, 256], hidden_size = 64, bidirectional = True, batch_size = None, device = 'cpu'):
        super().__init__()
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=lookback, batch_first=True, bidirectional=bidirectional, dropout=0.1)
        self.num_layers = lookback
        # assert layers[-1] == 2, "The last layer must have 2 output units for the x and y coordinates"
        self.bi = 2 if bidirectional else 1
        neuron_num = hidden_size * 2 + hidden_size * self.bi
        
        if batch_size is None:
            raise ValueError("Please provide the batch size")
        else: 
            self.batch_size = batch_size
        
        self.h_0 = Variable(torch.zeros(self.num_layers * self.bi, batch_size, hidden_size, device=device)) #hidden state
        self.c_0 = Variable(torch.zeros(self.num_layers * self.bi, batch_size, hidden_size, device=device)) #internal state
        
        mlp_layers = []
        in_features = neuron_num
        layers.append(input_size)
        for out_features in layers:
            mlp_layers.append(nn.Linear(in_features, out_features))
            mlp_layers.append(nn.ReLU())  # Adding ReLU activation function after each Linear layer
            mlp_layers.append(nn.Dropout(0.2))  # Adding dropout layer
            in_features = out_features  # Update in_features for the next layer
        
        mlp_layers.pop() # Remove the last ReLU added in the loop
        mlp_layers.pop() # Remove the last Dropout added in the loop
        
        self.mlp = nn.Sequential(*mlp_layers)


    def forward(self, x): 
        if x.shape[0] != self.batch_size:
            raise ValueError(f"Batch size mismatch. Expected {self.batch_size} but got {x.shape[0]}")
        
        lstm_out, (h_n, c_n) = self.lstm(x, (self.h_0, self.c_0))
        batch_first_hidden = torch.cat((c_n.permute(1, 0, 2), h_n.permute(1, 0, 2)), dim=2)
        last_batch_hidden = batch_first_hidden[:, -1, :]
        last_out = lstm_out[:, -1, :]
        latent_all = torch.cat((last_batch_hidden, last_out), dim=1)

        out = self.mlp(latent_all)
        return out