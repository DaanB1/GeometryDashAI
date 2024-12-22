# GeometryDashAI
This repo contains the code I used to make the first working neural network inside the game Geometry Dash. The model has been trained externally and its weights have been saved in a file. Using [NeditGD](https://github.com/Boris-Filin/NeditGD), the structure of the convolutional neural network is recreated in the form of Geometry Dash triggers. The 'Item Edit' trigger performs multiplications according to the specified weights, and adds the results together. The 'Item Compare' trigger is used to recreate the ReLU activation function. The end result is a fully working convolutional neural network capable of recognizing handwritten digits. 

#### Level information:
- Name: Brain Game
- ID: 102017933
