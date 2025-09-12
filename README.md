[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()

## 🎹 Piano Virtual com Visão Computacional

Um simulador de piano interativo que usa visão computacional (OpenCV) para detectar movimentos das mãos e reproduzir notas musicais com o Pygame.

Este repositório contém uma versão experimental (em `playground/`) de um piano virtual que permite tocar notas e acordes usando gestos capturados pela webcam.

## 🎯 Recursos principais

- Detecção de movimento em tempo real usando OpenCV
- Interface simples com Pygame para reprodução de áudio
- Sons reais de piano (arquivos WAV) para diferentes teclas
- Suporte a múltiplas teclas ao mesmo tempo (acordes)
- Calibração interativa para mapear teclas na imagem da câmera
- Estrutura simples para experimentar e estender
- Gravação e reprodução de sequências de notas
- Interface gráfica para ajustar volume e sensibilidade

## 📋 Pré-requisitos

- Python 3.12 ou superior
- Webcam funcional
- Dependências listadas em `pyproject.toml`
- Recomenda-se criar e ativar um virtualenv (ex.: venv, .venv)

## 🚀 Instalação rápida

1. Clone o repositório:

```powershell
git clone https://github.com/jvras58/xxxxxxx
cd python-piano
```

2. Crie e ative um ambiente virtual (opcional, recomendado):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

3. Instale dependências.

Se você usa o gerenciador `uv` (mencionado no projeto):

```powershell
uv sync
```

Ou instale manualmente com pip (se preferir):

```powershell
python -m pip install -r requirements.txt
```

Obs: se `requirements.txt` não existir, instale pelo `pyproject.toml` ou instale manualmente `opencv-python` e `pygame`.

## ▶️ Como executar

Execute o script principal:

```powershell
python main.py
```

Ao iniciar, posicione a webcam de modo que a área das teclas esteja visível.

## 🎛️ Controles e Calibração

- Pressione `q` para sair.
- Pressione `r` para entrar no modo de calibração.
    - Em modo de calibração, use `c` para confirmar a posição da tecla atual.
    - Use `n` para avançar para a próxima tecla.
- Toque nas regiões da imagem para tocar as notas (dependendo da implementação do arquivo em `playground/`).

Dica: siga as instruções exibidas na janela do programa durante a calibração.

- Pressione 'g' para iniciar/parar gravação
- Pressione 'p' para iniciar/parar reprodução
- Pressione 's' para abrir menu de configurações

## 🧭 Estrutura do projeto

```
python-drums/
├── main.py            # Ponto de entrada principal
├── README.md          # Documentação (este arquivo)
├── pyproject.toml     # Dependências do projeto
├── playground/        # Experimentais: piano, teclas, virtual
│   ├── virtual_piano.py
│   ├── piano.py
│   └── key.py
└── sounds/            # Arquivos WAV usados pelo projeto(Baixados pelo freesound.org)
```

## 🛠️ Dicas de desenvolvimento

- Se o áudio não tocar, verifique se os arquivos WAV estão no diretório `sounds/`.
- Teste a webcam com o OpenCV separadamente para garantir que o dispositivo está acessível.
- Para ajustar sensibilidade de detecção, procure parâmetros no código em `playground/`.

## 🐞 Solução de problemas rápidos

- Erro ao abrir a câmera: verifique o ID do dispositivo e se outro programa não está usando a webcam.
- Dependências não encontradas: ative o ambiente virtual e rode a instalação novamente.
- Latência de áudio/entrada: feche outros programas que consomem CPU/GPU e teste com resoluções menores.

## 🤝 Contribuição

Contribuições são bem-vindas. Abra uma issue para discutir ideias ou envie um pull request contendo:

- Descrição clara do que muda
- Testes ou instruções para validar
- Arquivos modificados