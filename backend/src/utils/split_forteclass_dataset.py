import pandas as pd
from sklearn.model_selection import train_test_split
import os

# Caminho do CSV original dentro do container
csv_path = "/app/dataset_forteclass_FULL.csv"

# Caminho da pasta onde você quer salvar os novos arquivos dentro do container
save_path = "/app/backend/src/dataset/forteclass_train_test"

# Garante que a pasta de destino exista (cria se não existir)
os.makedirs(save_path, exist_ok=True)

# Carregar o CSV
df = pd.read_csv(csv_path)

# Dividir em 90% treino e 10% teste
train_df, test_df = train_test_split(df, test_size=0.1, random_state=42, shuffle=True)

# Monta os caminhos completos para salvar
train_file = os.path.join(save_path, "train_dataset.csv")
test_file = os.path.join(save_path, "test_dataset.csv")

# Salvar os arquivos
train_df.to_csv(train_file, index=False)
test_df.to_csv(test_file, index=False)

print("Dataset dividido com sucesso!")
print(f"Treino salvo em: {train_file} ({len(train_df)} linhas)")
print(f"Teste salvo em: {test_file} ({len(test_df)} linhas)")
