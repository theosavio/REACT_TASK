import torch
print(torch.cuda.is_available())  # This should return True
print(torch.cuda.device_count())   # This should return the number of GPUs available
