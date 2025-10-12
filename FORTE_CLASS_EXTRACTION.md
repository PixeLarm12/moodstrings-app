# Extração de Forte Classes - Dataset MIDI

## 📋 Resumo

Este commit implementa a funcionalidade de **extração de Forte Classes** de arquivos MIDI para criação de datasets de Machine Learning. O script `process_xmidi_dataset.py` foi desenvolvido para processar arquivos MIDI e extrair as classes de acordes (Forte Classes) que serão utilizadas como features para treinamento de IA.

## 🎯 Objetivo

Extrair **Forte Classes** (representação teórica musical de acordes) de arquivos MIDI para criar um dataset estruturado que será usado no treinamento de modelos de IA para classificação de emoções em música.

## ⚠️ Status Atual - COMMIT DE TESTE

**Este commit processa apenas uma AMOSTRA de 15 arquivos** para validação da implementação. O próximo commit incluirá um script otimizado para processar **todo o dataset base**.

## 🛠️ O que foi implementado

### 1. Script de Processamento
- **Arquivo**: `process_xmidi_dataset.py`
- **Funcionalidade**: Extrai Forte Classes dos primeiros 15 arquivos MIDI
- **Output**: CSV com filename, emotion, genre, file_id, forteclass_sequence, num_classes

### 2. Backend - Métodos de Apoio
- **MidiService.py**: Método para extração de Forte Classes
- **DatasetService.py**: Lógica de processamento em lote
- **AdminController.py**: Endpoint REST para processamento via API

### 3. Configuração Docker
- **Volume mapping**: Mapeamento da pasta local de MIDI files
- **Environment**: Configuração de paths via `.env`

## 🚀 Como usar este script

### Pré-requisitos

1. **Docker** instalado e funcionando
2. **Dataset MIDI** em pasta local (ex: `C:\temp\XMIDI_Dataset`)
3. **Repositório clonado** e Docker Compose configurado

### Passos para execução

#### 1. Clone o repositório
```bash
git clone https://github.com/PixeLarm12/moodstrings-app.git
cd moodstrings-app
git checkout feature/forteclass-extraction
```

#### 2. Configure o arquivo .env
Crie/edite o arquivo `.env` na raiz do projeto:

```env
# Mapeamento da pasta que contém os arquivos MIDI
MIDI_FILES_FROM_PATH=C:\temp\XMIDI_Dataset

# Outras configurações do projeto...
```

**⚠️ Importante**: Ajuste o caminho `MIDI_FILES_FROM_PATH` para onde estão seus arquivos MIDI locais.

#### 3. Suba os containers
```bash
docker-compose up --build
```

#### 4. Copie o script para o container
```bash
docker cp process_xmidi_dataset.py moodstrings-app-backend-1:/app/
```

#### 5. Execute o script
```bash
docker exec -it moodstrings-app-backend-1 python /app/process_xmidi_dataset.py
```

### 📊 Output esperado

O script irá:
1. **Buscar** arquivos MIDI na pasta mapeada (`/app/midi_raw_files` no container)
2. **Processar** os primeiros 15 arquivos encontrados
3. **Extrair** as Forte Classes de cada arquivo
4. **Gerar** um CSV com os resultados: `dataset_forteclass_15.csv`
5. **Mostrar** estatísticas detalhadas no terminal

#### Exemplo de output no terminal:
```
Encontrados 108023 arquivos MIDI
Processando os primeiros 15 arquivos...

Processando: XMIDI_angry_classical_0631TTPB.midi
  - Emoção: angry, Gênero: classical, ID: 0631TTPB
  - Forte Classes extraídas: 82
  - Primeiras classes: 1-1,3-11B,1-1,3-11B,2-2...

[... mais arquivos ...]

✅ Dataset salvo em: dataset_forteclass_15.csv
📊 Total de linhas no dataset: 15
```

#### Estrutura do CSV gerado:
```csv
filename,emotion,genre,file_id,forteclass_sequence,num_classes
XMIDI_angry_classical_0631TTPB.midi,angry,classical,0631TTPB,"1-1,3-11B,1-1,3-11B,2-2...",82
```

## 🔧 Configuração para seu dataset

### Estrutura esperada dos arquivos MIDI:
```
MIDI_FILES_FROM_PATH/
├── XMIDI_angry_classical_001.midi
├── XMIDI_happy_jazz_002.midi
├── XMIDI_sad_rock_003.midi
└── ... (outros arquivos)
```

### Padrão de nomenclatura:
O script extrai automaticamente:
- **Emoção**: da palavra após "XMIDI_" (angry, happy, sad, etc.)
- **Gênero**: da palavra após a emoção (classical, jazz, rock, etc.)
- **ID único**: do final do filename (antes da extensão)

## 📈 Próximos passos

### Commit atual (TESTE)
- ✅ Processamento de **15 arquivos** para validação
- ✅ Validação da extração de Forte Classes
- ✅ Geração de CSV estruturado

### Próximo commit (PRODUÇÃO)
- 🔄 Script otimizado para **processamento completo**
- 🔄 Processamento de **todo o dataset base**
- 🔄 Melhorias de performance e logging
- 🔄 Validação e limpeza de dados em larga escala

## 🐛 Troubleshooting

### Problema: "No such file or directory"
- **Causa**: Caminho do MIDI_FILES_FROM_PATH incorreto no `.env`
- **Solução**: Verifique se o caminho existe e está acessível

### Problema: "Container not found"
- **Causa**: Containers não estão rodando
- **Solução**: Execute `docker-compose up --build`

### Problema: "Permission denied"
- **Causa**: Problemas de permissão no volume Docker
- **Solução**: Verifique as permissões da pasta local

### Problema: Script não encontrado no container
- **Causa**: Script não foi copiado para o container
- **Solução**: Execute `docker cp process_xmidi_dataset.py moodstrings-app-backend-1:/app/`

## 🔍 Detalhes técnicos

### Dependências utilizadas:
- **music21**: Para análise musical e extração de Forte Classes
- **pretty_midi**: Para parsing de arquivos MIDI
- **pandas**: Para manipulação e export de dados

### Método de extração:
1. **Parse MIDI**: Carregamento do arquivo com pretty_midi
2. **Análise harmônica**: Identificação de acordes por janelas de tempo
3. **Forte Classification**: Conversão para notação de classes de acordes
4. **Serialização**: Concatenação das classes em sequência temporal

---

**🎵 Este é um passo importante para a criação de um dataset rico em features musicais teóricas para treinamento de IA emocional!**