import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import sounddevice as sd
import threading
import os
import sounddevice as sd
from player import SineWavePlayer
from streamlit.runtime.scriptrunner import add_script_run_ctx


L = 1.0  # długość struny
Nx = 200  # liczba punktów w przestrzeni
dx = L / (Nx - 1)  # krok w przestrzeni
Nt = 5000  # liczba kroków czasowych
dt = 0.004    # krok czasowy
# dzwiek
FREQUENCY = 440


def init_string_state():
    st.session_state.y = np.zeros(Nx)  
    st.session_state.y_new = np.zeros(Nx)
    st.session_state.y_old = np.zeros(Nx)
    st.session_state.simulation_started = False
    st.session_state["player"] = SineWavePlayer(FREQUENCY)


def start_wave():
    for i in range(Nx): 
        if 40 <= i < 60:  # szarpnięcie w oknie od 40 do 60
            st.session_state.y[i] = 0.5 * np.sin(np.pi * (i - 40) / 20)
    st.session_state.y_old[:] = st.session_state.y 


def update(T, mu, b):
    for i in range(1, Nx - 1):
        # Zdyskretyzowane rownanie falowe
        st.session_state.y_new[i] = (
            2 * st.session_state.y[i] 
            - st.session_state.y_old[i] 
            + (T / mu) * dt**2 / dx**2 * (st.session_state.y[i+1] - 2 * st.session_state.y[i] + st.session_state.y[i-1])
            - b * dt / mu * (st.session_state.y[i] - st.session_state.y_old[i])
        )
    amplitude = np.max(np.abs(st.session_state.y_new))
    st.session_state["player"].set_amplitude(amplitude)
    st.session_state.y_old[:] = st.session_state.y
    st.session_state.y[:] = st.session_state.y_new


def visualization(): 
    if 'y' not in st.session_state:
        init_string_state()

    st.sidebar.title("Parametry struny")
    T = st.sidebar.slider("Napięcie struny (T)", 0.1, 5.0, 1.0, 0.1)  # slider dla napięcia
    mu = st.sidebar.slider("Gęstość liniowa (μ)", 0.01, 1.0, 0.1, 0.01)  # slider dla gęstości
    b = st.sidebar.slider("Współczynnik tłumienia (b)", 0.0, 5.0, 0.1, 0.01)  # slider dla tłumienia
    player_thread = None

    st.title('Symulacja fali poprzecznej na strunie')

    if st.sidebar.button("Resetuj symulację") and st.session_state.simulation_started:
        st.session_state["player"].stop()
        init_string_state()
        
        
    if st.button('Start') and not st.session_state.simulation_started:
        start_wave()
        st.session_state.simulation_started = True
        if not st.session_state["player"].playing:
            player_thread = threading.Thread(target=st.session_state["player"].start, daemon=True)
            player_thread.start()
            add_script_run_ctx(st.session_state["player"])
            

    if st.session_state.simulation_started:
        placeholder = st.empty()
        
        for _ in range(Nt):
            fig, ax = plt.subplots()
            ax.plot(np.linspace(0, L, Nx), st.session_state.y)  
            ax.set_ylim([-1.5, 1.5])
            ax.set_title('Symulacja fali poprzecznej na strunie')
            ax.set_xlabel('x (m)')
            ax.set_ylabel('y (m)')
            
            placeholder.pyplot(fig)
            
            plt.close(fig)
            
            update(T=T, mu=mu,b=b)
    else:
        fig, ax = plt.subplots()
        ax.plot(np.linspace(0, L, Nx), st.session_state.y)
        ax.set_ylim([-1.5, 1.5])
        ax.set_title('Symulacja fali poprzecznej na strunie')
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        
        st.pyplot(fig)
        plt.close(fig)

if __name__ == "__main__":
    visualization()