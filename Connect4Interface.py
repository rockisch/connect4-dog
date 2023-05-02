import tkinter as tk
from tkinter import ttk, N, E, W, S, font as tkFont
from typing import Dict, Optional
from uuid import UUID
from PIL import Image, ImageTk, ImageDraw

from py_netgames_client.tkinter_client.PyNetgamesServerListener import (
    PyNetgamesServerListener,
)
from py_netgames_client.tkinter_client.PyNetgamesServerProxy import (
    PyNetgamesServerProxy,
)
from py_netgames_model.messaging.message import MatchStartedMessage, MoveMessage

from game_logic.Tabuleiro import Tabuleiro, SlotState, MAX_X, MAX_Y


BASE_STYLE = "Base.TFrame"
ACTION_BUTTON_STYLE = "Action.TButton"


EMPTY_COLOR = (255, 255, 255)
P1_COLOR = (255, 0, 0)
P2_COLOR = (255, 255, 0)


SLOT_SIZE = 70
SLOT_PAD = 10
SLOT_FULL = SLOT_SIZE + SLOT_PAD
AA_SCALE = 4
AA_SLOT_SIZE = SLOT_SIZE * AA_SCALE
AA_SLOT_PAD = SLOT_PAD * AA_SCALE
AA_SLOT_FULL = AA_SLOT_SIZE + AA_SLOT_PAD


class Connect4Interface(PyNetgamesServerListener):
    match_id: Optional[str]
    server_proxy: PyNetgamesServerProxy
    board: Optional[Tabuleiro]

    tk: tk.Tk
    _mainframe: ttk.Frame
    _current_screen: ttk.Frame
    _connect_button: Optional[ttk.Button]
    _start_button: Optional[ttk.Button]

    def __init__(self) -> None:
        super().__init__()

        self.match_id = None
        self.server_proxy = PyNetgamesServerProxy()
        self.board = None

        self.tk = tk.Tk()
        ttk.Style().configure(BASE_STYLE, background="lightblue")
        ttk.Style().configure(ACTION_BUTTON_STYLE, background="lightblue")
        self.tk.rowconfigure(0, weight=1)
        self.tk.columnconfigure(0, weight=1)
        self.tk.title("Connect 4")
        self.tk.geometry("1280x720")
        self.tk.resizable(width=False, height=False)
        self._mainframe = ttk.Frame(self.tk, style=BASE_STYLE)
        self._mainframe.grid(sticky="news")
        self._mainframe.rowconfigure(0, weight=1)
        self._mainframe.columnconfigure(0, weight=1)
        self._current_screen = ttk.Frame(self._mainframe)
        self._connect_button = None
        self._start_button = None

    def render_menu(self):
        menu_screen = ttk.Frame(
            self._mainframe,
            style="Base.TFrame",
            padding="100",
        )
        render = ImageTk.PhotoImage(Image.open("assets/logo.png"))
        # Weird behavior with 'Pillow' where
        label = ttk.Label(
            menu_screen, text="Connect 4", image=render, background="lightblue"
        )
        label.image = render
        label.grid(row=0, column=0)
        self._connect_button = ttk.Button(
            menu_screen,
            text="Connect",
            padding="15 10",
            command=self.connect,
        )
        self._connect_button.grid(row=1, column=0, pady=5)
        self._start_button = ttk.Button(
            menu_screen,
            text="Match",
            padding="15 10",
            command=self.start_match,
        )
        self._start_button.state(["disabled"])
        self._start_button.grid(row=2, column=0, pady=5)
        menu_screen.grid(row=0, column=0)
        self._current_screen.grid_forget()
        self._current_screen = menu_screen

    def render_game(self):
        game_screen = ttk.Frame(self._mainframe, style=BASE_STYLE)
        p1_frame = ttk.Frame(game_screen, style=BASE_STYLE)
        p2_frame = ttk.Frame(game_screen, style=BASE_STYLE)
        ttk.Label(
            p1_frame,
            text="P1",
            padding="15 10",
        ).grid(row=0, column=0, sticky=N)
        ttk.Label(
            p2_frame,
            text="P2",
            padding="15 10",
        ).grid(row=0, column=0, sticky=N)
        ttk.Label(
            p1_frame,
            text="^",
            padding="15 10",
        ).grid(row=1, column=0, sticky=N, pady=20)
        p1_frame.grid(row=0, column=0, sticky=N)
        p2_frame.grid(row=0, column=2, sticky=N)
        board_image = ImageTk.PhotoImage(self._get_board_image())
        board_frame = ttk.Frame(
            game_screen,
            style=BASE_STYLE,
            width=board_image.width(),
            height=board_image.height(),
        )
        buttons = ttk.Frame(board_frame, style=BASE_STYLE)
        for x in range(MAX_X):
            button = ttk.Button(buttons, text="↓", style=ACTION_BUTTON_STYLE)
            button.grid(row=0, column=x, padx=2)

        buttons.grid(row=0, column=0, columnspan=MAX_X)
        board_element = ttk.Label(
            board_frame, image=board_image, background="lightblue"
        )
        board_element.image = board_image
        board_element.grid(row=1, column=0, rowspan=MAX_Y, columnspan=MAX_X)

        board_frame.grid(row=0, column=1, rowspan=MAX_Y)

        game_screen.grid(row=0, column=0)
        self._current_screen.grid_forget()
        self._current_screen = game_screen

    def _get_board_image(self) -> Image.Image:
        bottom_size_pad = 100
        bottom_pad = 100
        outline_pad = 20
        side_pad = AA_SLOT_PAD + bottom_size_pad
        size = (
            (MAX_X * AA_SLOT_FULL) + AA_SLOT_PAD + (bottom_size_pad * 2),
            (MAX_Y * AA_SLOT_FULL) + AA_SLOT_PAD + bottom_pad,
        )
        im = Image.new(
            mode="RGBA",
            size=size,
        )
        draw = ImageDraw.Draw(im)
        draw.rectangle(
            (bottom_size_pad, 0, size[0] - bottom_size_pad, size[1]), fill=(20, 20, 255)
        )
        draw.rectangle(
            (0, size[1] - bottom_pad, size[0], size[1]),
            fill=(20, 20, 255),
        )
        for x in range(MAX_X):
            for y in range(MAX_Y):
                match self.board.get_position(x, y):
                    case SlotState.EMPTY:
                        color = EMPTY_COLOR
                        outline = False
                    case SlotState.P1:
                        color = P1_COLOR
                        outline = True
                    case SlotState.P2:
                        color = P2_COLOR
                        outline = True

                x0 = side_pad + (x * AA_SLOT_FULL)
                y0 = AA_SLOT_PAD + (y * AA_SLOT_FULL)
                draw.ellipse(
                    (
                        x0,
                        y0,
                        (x0 + AA_SLOT_SIZE),
                        (y0 + AA_SLOT_SIZE),
                    ),
                    fill=color,
                )
                if outline:
                    draw.ellipse(
                        (
                            x0 + outline_pad,
                            y0 + outline_pad,
                            (x0 + AA_SLOT_SIZE) - outline_pad,
                            (y0 + AA_SLOT_SIZE) - outline_pad,
                        ),
                        outline=(0, 0, 0),
                    )

        return im.resize(
            (int(size[0] / AA_SCALE), int(size[1] / AA_SCALE)), resample=Image.ANTIALIAS
        )

    def run(self):
        self.server_proxy.add_listener(self)
        self.render_menu()
        self.tk.mainloop()

    def connect(self):
        self._connect_button["text"] = "Connecting"
        self._connect_button.state(["disabled"])
        self.server_proxy.send_connect(address="wss://py-netgames-server.fly.dev")

    def start_match(self):
        self._start_button["text"] = "Searching"
        self._start_button.state(["disabled"])
        self.server_proxy.send_match(amount_of_players=2)

    def receive_connection_success(self):
        self._connect_button["text"] = "Connected"
        self._start_button.state(["!disabled"])

    def receive_match(self, match):
        self.match_id = match.match_id
        print("PARTIDA INICIADA")
        print("ORDEM : %s" % str(match.position))
        print("MATCH ID : %s" % str(match.match_id))
        self.board = Tabuleiro()
        self.render_game()

    def send_match(self):
        self.server_proxy.send_match(2)

    def receive_move(self, message: MoveMessage):
        raise NotImplementedError

    def receive_error(self, error):
        raise NotImplementedError

    def receive_disconnect(self):
        raise NotImplementedError

    # def receive_move_sent_success(self):
    #     raise NotImplementedError
