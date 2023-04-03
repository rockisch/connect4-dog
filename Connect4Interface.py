import logging
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
    server_proxy: PyNetgamesServerProxy
    logger: logging.Logger

    tk: tk.Tk
    mainframe = ttk.Frame
    current_frame = ttk.Frame

    match_id: Optional[str]
    board: Optional[Tabuleiro]

    def __init__(self) -> None:
        super().__init__()

        self.server_proxy = PyNetgamesServerProxy()
        self.logger = logging.getLogger("Connect4Interface")

        self.tk = tk.Tk()
        ttk.Style().configure(BASE_STYLE, background="lightblue")
        ttk.Style().configure(ACTION_BUTTON_STYLE, background="lightblue")
        self.tk.rowconfigure(0, weight=1)
        self.tk.columnconfigure(0, weight=1)
        self.tk.title("Connect 4")
        self.tk.geometry("1280x720")
        self.tk.resizable(width=False, height=False)
        self.mainframe = ttk.Frame(self.tk, style=BASE_STYLE)
        self.mainframe.grid(sticky="news")
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.columnconfigure(0, weight=1)
        self.current_frame = ttk.Frame(self.mainframe)

        self.match_id = None
        self.board = None
        self.start_button = None

    def render_menu(self):
        menu_frame = ttk.Frame(
            self.mainframe,
            style="Base.TFrame",
            padding="100",
        )
        render = ImageTk.PhotoImage(Image.open("assets/logo.png"))
        # Weird behavior with 'Pillow' where
        label = ttk.Label(
            menu_frame, text="Connect 4", image=render, background="lightblue"
        )
        label.image = render
        label.grid(row=0, column=0)
        self.connect_button = ttk.Button(
            menu_frame,
            text="Connect",
            padding="15 10",
            command=self.connect,
        )
        self.connect_button.grid(row=1, column=0, pady=5)
        self.start_button = ttk.Button(
            menu_frame,
            text="Match",
            padding="15 10",
            command=self.start_match,
        )
        self.start_button.state(["disabled"])
        self.start_button.grid(row=2, column=0, pady=5)
        ttk.Button(
            menu_frame,
            text="Exit",
            padding="15 10",
            command=self.exit_game,
        ).grid(row=3, column=0, pady=5)
        ttk.Button(
            menu_frame,
            text="Go To Game (temporary)",
            padding="15 10",
            command=self._syntetic_receive_match,
        ).grid(row=4, column=0, pady=5)
        menu_frame.grid(row=0, column=0)
        self.current_frame.grid_forget()
        self.current_frame = menu_frame

    def render_game(self):
        game_frame = ttk.Frame(self.mainframe, style=BASE_STYLE)
        p1_frame = ttk.Frame(game_frame, style=BASE_STYLE)
        p2_frame = ttk.Frame(game_frame, style=BASE_STYLE)
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
        board_image = ImageTk.PhotoImage(self.render_game_canvas())
        board_frame = ttk.Frame(
            game_frame,
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

        game_frame.grid(row=0, column=0)
        self.current_frame.grid_forget()
        self.current_frame = game_frame

    def render_game_canvas(self) -> Image.Image:
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
        self.connect_button["text"] = "Connecting"
        self.connect_button.state(["disabled"])
        self.server_proxy.send_connect(address="wss://py-netgames-server.fly.dev")

    def start_match(self):
        self.start_button["text"] = "Searching"
        self.start_button.state(["disabled"])
        self.server_proxy.send_match(amount_of_players=2)

    def exit_game(self):
        exit(0)

    def _syntetic_receive_match(self):
        m = MatchStartedMessage(self.match_id, 0)
        self.receive_match(m)

    def receive_connection_success(self):
        self.connect_button["text"] = "Connected"
        self.start_button.state(["!disabled"])

    def receive_match(self, message: MatchStartedMessage):
        self.match_id = message.match_id
        self.board = Tabuleiro()
        self.render_game()

    def receive_move(self, message: MoveMessage):
        raise NotImplemented

    def receive_error(self, error):
        raise NotImplemented

    def receive_disconnect(self):
        raise NotImplemented
