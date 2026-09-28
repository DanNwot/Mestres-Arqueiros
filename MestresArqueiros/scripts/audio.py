"""
Mestres Arqueiros — Gerenciador de Áudio
Sistema resiliente que carrega sons e músicas com fallback automático.
"""

import os
import pygame


class AudioManager:
    """Gerencia toda a reprodução de áudio do jogo com fallback seguro e pré-carregamento."""

    def __init__(self, settings):
        self.settings = settings
        self.initialized = False
        self.sounds = {}
        self.current_music_path = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.initialized = True
            self._preload_sounds()
        except Exception as e:
            print(f"[AudioManager] Aviso: Não foi possível inicializar áudio: {e}")
            self.initialized = False

    def _preload_sounds(self):
        """Carrega todos os arquivos de som padrão da pasta assets/sounds."""
        if not self.initialized:
            return
            
        sounds_dir = os.path.join("assets", "sounds")
        if not os.path.exists(sounds_dir):
            return

        sound_names = ["shoot", "hit", "headshot", "explosion", "dirt", "click", "victory", "defeat"]
        for name in sound_names:
            for ext in [".wav", ".ogg", ".mp3"]:
                sound_path = os.path.join(sounds_dir, f"{name}{ext}")
                if os.path.exists(sound_path):
                    self.load_sound(name, sound_path)
                    break

    # -----------------------------------------------------------------
    # Efeitos sonoros
    # -----------------------------------------------------------------
    def load_sound(self, name, path):
        """Carrega um efeito sonoro. Ignora silenciosamente se falhar."""
        if not self.initialized:
            return
        try:
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"[AudioManager] Falha ao carregar som {name} ({path}): {e}")

    def play_sound(self, name):
        """Reproduz um efeito sonoro previamente carregado."""
        if not self.initialized or self.settings.sfx_volume <= 0:
            return
        sound = self.sounds.get(name)
        if sound is None:
            # Tenta carregar sob demanda
            for ext in [".wav", ".ogg", ".mp3"]:
                p = os.path.join("assets", "sounds", f"{name}{ext}")
                if os.path.exists(p):
                    self.load_sound(name, p)
                    sound = self.sounds.get(name)
                    break

        if sound:
            try:
                sound.set_volume(self.settings.sfx_volume)
                sound.play()
            except Exception:
                pass

    # -----------------------------------------------------------------
    # Música de fundo
    # -----------------------------------------------------------------
    def play_music(self, path):
        """Reproduz música em loop. Suporta fallback .ogg <-> .wav."""
        if not self.initialized:
            return
            
        # Fallback de extensão se arquivo não existir
        actual_path = path
        if not os.path.exists(actual_path):
            base, ext = os.path.splitext(path)
            alt_ext = ".wav" if ext == ".ogg" else ".ogg"
            alt_path = base + alt_ext
            if os.path.exists(alt_path):
                actual_path = alt_path

        if not os.path.exists(actual_path):
            return

        if self.current_music_path == actual_path and pygame.mixer.music.get_busy():
            return

        self.current_music_path = actual_path

        if not self.settings.music_on:
            return

        try:
            pygame.mixer.music.load(actual_path)
            pygame.mixer.music.set_volume(self.settings.music_volume)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[AudioManager] Erro ao tocar música {actual_path}: {e}")

    def stop_music(self):
        """Para a música de fundo."""
        if not self.initialized:
            return
        try:
            pygame.mixer.music.stop()
            self.current_music_path = None
        except Exception:
            pass

    def update_volumes(self):
        """Atualiza os volumes de música conforme configurações atuais."""
        if not self.initialized:
            return
        try:
            vol = self.settings.music_volume if self.settings.music_on else 0.0
            pygame.mixer.music.set_volume(vol)
            if self.settings.music_on and not pygame.mixer.music.get_busy() and self.current_music_path:
                self.play_music(self.current_music_path)
            elif not self.settings.music_on:
                pygame.mixer.music.stop()
        except Exception:
            pass

    def toggle_music(self):
        """Liga/desliga a música e atualiza o volume."""
        self.settings.music_on = not self.settings.music_on
        self.update_volumes()
