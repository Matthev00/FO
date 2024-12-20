# Opis projektu
Projekt symuluje wizualnie oraz dźwiękowo falę poprzeczną na strunie z uwzględnieniem tłumienia energii. Użytkownik może regulować napięcie struny oraz współczynnik tłumienia za pomocą interfejsu aplikacji.

Rozbudowano projekt o:
- **Analizę widma częstotliwości (FFT):** umożliwia identyfikację dominujących harmonicznych i wizualizację widma.
- **Synchronizację dźwięku z FFT:** generowanie dźwięku w czasie rzeczywistym opartego na dominujących harmonicznych.

# Model matematyczny 
1. Równanie falowe

$$
\frac{\partial^2 y}{\partial t^2} = \frac{T}{\mu} \frac{\partial^2 y}{\partial x^2} - b \frac{\partial y}{\partial t}
$$
​
gdzie:  
T to napięcie struny,  
$\mu$ to gęstość liniowa struny,  
b to współczynnik tłumienia.

# Dyskretyzacja

$$
y(i, t + \Delta t) = 2y(i, t) - y(i, t - \Delta t) + \frac{T}{\mu} \frac{\Delta t^2}{{\Delta x^2}} (y(i + 1, t) - 2y(i, t) + y(i - 1, t)) - \frac{b \Delta t}{\mu} (y(i, t) - y(i, t - \Delta t))
$$
Dyskretyzacja metodą różnic skończonych

# Uruchomienie
1. ```sh
    git clone https://github.com/Matthev00/FO
    ```
2. 
    ```sh
    python3 -m venv .venv
    ```
3. 
    ``` sh
    source .venv/bin/activate
    ```
3. 
    ``` sh
    pip install -r requirements.txt
    ```
4. 
    ```sh 
    streamlit run main.py
    ```

# Modele generatywne AI
- ChatGPT 4o - aspekty streamlit, wielowątkowość
- Copilot - model był włączony w IDE 

# Źródła
https://dspace.mit.edu/bitstream/handle/1721.1/111950/2-062j-fall-2006/contents/lecture-notes/lect1.pdf
