import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import sounddevice as sd
import threading
from player import SineWavePlayer
from streamlit.runtime.scriptrunner import add_script_run_ctx

L = 1.0  # długość struny
Nx = 200  # liczba punktów w przestrzeni
dx = L / (Nx - 1)  # krok w przestrzeni
Nt = 5000  # liczba kroków czasowych
dt = 0.001  # krok czasowy
mu = 2  # gęstość liniowa struny
# dzwiek
FREQUENCY = 0


def init_string_state():
    st.session_state.y = np.zeros(Nx)
    st.session_state.y_new = np.zeros(Nx)
    st.session_state.y_old = np.zeros(Nx)
    st.session_state.simulation_started = False
    st.session_state["player"] = SineWavePlayer(FREQUENCY)


def start_wave():
    st.session_state.y[:] = 0.0
    st.session_state.y_old[:] = 0.0

    # Szarpnięcie
    for i in range(40, 60):
        st.session_state.y[i] = 0.5 * np.sin(4 * np.pi * (i - 40) / 20)
    st.session_state.y_old[:] = st.session_state.y


def compute_fft(signal) -> tuple[np.ndarray, np.ndarray]:
    """Oblicza FFT dla sygnału."""
    N = len(signal)
    fft_values = np.fft.fft(signal)
    fft_magnitude = np.abs(fft_values[: N // 2])
    freqs = np.fft.fftfreq(N, d=dt)[: N // 2]
    return freqs, fft_magnitude


def update(T, mu, b):
    """Aktualizuje stan struny i dźwięku oraz oblicza FFT."""
    for i in range(1, Nx - 1):
        # Zdyskretyzowane równanie falowe
        st.session_state.y_new[i] = (
            2 * st.session_state.y[i]
            - st.session_state.y_old[i]
            + (T / mu)
            * dt**2
            / dx**2
            * (
                st.session_state.y[i + 1]
                - 2 * st.session_state.y[i]
                + st.session_state.y[i - 1]
            )
            - b * dt / mu * (st.session_state.y[i] - st.session_state.y_old[i])
        )

    freqs, fft_magnitude = compute_fft(st.session_state.y_new)

    if "fft_plot" not in st.session_state:
        st.session_state.fft_plot = st.empty()

    fig_fft, ax_fft = plt.subplots()
    ax_fft.plot(freqs, fft_magnitude)
    ax_fft.set_title("Widmo częstotliwości")
    ax_fft.set_xlabel("Częstotliwość (Hz)")
    ax_fft.set_ylabel("Amplituda")
    ax_fft.set_ylim([0, 5])

    # Linie oznaczające mody własne
    v = np.sqrt(T / mu)  # prędkość propagacji fali
    modes = [n * v / (2 * L) for n in range(1, 1000, 100)]
    for mode in modes:
        ax_fft.axvline(
            x=mode, color="red", linestyle="--", label=f"Mod {modes.index(mode) + 1}"
        )
    ax_fft.legend()

    st.session_state.fft_plot.pyplot(fig_fft)
    plt.close(fig_fft)

    # Najmocniejsze harmoniczne z FFT
    dominant_modes = freqs[np.argsort(-fft_magnitude)[:3]]
    amplitudes = fft_magnitude[np.argsort(-fft_magnitude)[:3]]
    st.session_state["player"].set_freq(dominant_modes[0])
    st.session_state["player"].set_amplitude(max(amplitudes) / len(dominant_modes))

    frequency = 100 * v / (2 * L)
    if "frequency_display" not in st.session_state:
        st.session_state.frequency_display = st.empty()
    st.session_state.frequency_display.write(f"Częstotliwość: {frequency:.2f} Hz")

    # Aktualizacja stanu struny
    st.session_state.y_old[:] = st.session_state.y
    st.session_state.y[:] = st.session_state.y_new


def visualization():
    """Wizualizuje symulację fali poprzecznej na strunie."""
    if "y" not in st.session_state:
        init_string_state()

    st.sidebar.title("Parametry struny")
    T = st.sidebar.slider("Napięcie struny (T)", 1.5, 50.0, 2.0, 1.0)
    b = st.sidebar.slider("Współczynnik tłumienia (b)", 10.0, 50.0, 1.0, 0.1)
    player_thread = None

    st.title("Symulacja fali poprzecznej na strunie")

    if st.sidebar.button("Resetuj symulację") and st.session_state.simulation_started:
        st.session_state["player"].stop()
        init_string_state()

    if st.button("Start") and not st.session_state.simulation_started:
        start_wave()
        st.session_state.simulation_started = True
        if not st.session_state["player"].playing:
            player_thread = threading.Thread(
                target=st.session_state["player"].start, daemon=True
            )
            player_thread.start()
            add_script_run_ctx(st.session_state["player"])

    if st.session_state.simulation_started:
        placeholder = st.empty()

        for _ in range(Nt):
            fig, ax = plt.subplots()
            ax.plot(np.linspace(0, L, Nx), st.session_state.y)
            ax.set_ylim([-1.5, 1.5])
            ax.set_title("Symulacja fali poprzecznej na strunie")
            ax.set_xlabel("x (m)")
            ax.set_ylabel("y (m)")

            placeholder.pyplot(fig)
            plt.close(fig)

            update(T=T, mu=mu, b=b)
    else:
        fig, ax = plt.subplots()
        ax.plot(np.linspace(0, L, Nx), st.session_state.y)
        ax.set_ylim([-1.5, 1.5])
        ax.set_title("Symulacja fali poprzecznej na strunie")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")

        st.pyplot(fig)
        plt.close(fig)


if __name__ == "__main__":
    visualization()
