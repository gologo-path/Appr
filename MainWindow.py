from tkinter import messagebox

from matplotlib.offsetbox import AnchoredText

from WindowPattern import WindowPattern
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class MainWindow(WindowPattern):
    start_x = []
    start_y = []
    _number_var = 0
    first = ""
    second = ""
    error_first = 0
    error_second = 0

    def __init__(self):
        super().__init__("Appr")

    def eval_P1(self, x):
        return eval(self.first.replace("x", "({})".format(x)))

    def eval_P2(self, x):
        return eval(self.second.replace("x", "({})".format(x)))

    def _open_command(self):
        super()._open_command()
        with open(self.file, "r") as f:
            lines = f.readlines()
            for item in lines[0].split(','):
                self.start_x.append(float(item))

            for item in lines[1].split(','):
                self.start_y.append(float(item))

        self._start_calculations()
        self._build_plot()

    def _new_command(self):
        super()._new_command()
        self.dialog_window = tk.Tk()
        self.dialog_window.geometry("300x100")
        self.dialog_window.resizable(False, False)
        label = tk.Label(self.dialog_window, text="Введите количество точек, но не больше 10",
                         font=("Times new Roman", 10))
        label.pack()
        self.spinbox = tk.Spinbox(self.dialog_window, from_=2, to=10, width=7, font="10")
        self.spinbox.bind('<Return>', self._set_number_var)
        self.spinbox.pack()
        button = tk.Button(self.dialog_window, text="Ввод", command=self._set_number_var, font="10")
        button.pack()

    def _set_number_var(self):
        inp_str = self.spinbox.get()
        if not inp_str.isdigit():
            messagebox.showerror("Ошибка", "Ожидается ввод числа")
        elif int(inp_str) > 10 or int(inp_str) < 2:
            messagebox.showerror("Ошибка", "Ожидается число в диапазоне от 2 до 10")
        else:
            self._number_var = int(inp_str)
            self.dialog_window.destroy()
            self._build_fields()

    def _build_fields(self):
        self.fields_x = [None for _ in range(0, self._number_var)]
        self.fields_y = [None for _ in range(0, self._number_var)]

        for x in range(0, self._number_var):
            self.fields_x[x] = tk.StringVar()
            tmp = tk.Entry(textvariable=self.fields_x[x], width=10)
            tmp.grid(row=0, column=x, padx=5, pady=5)
            super()._destroyable_objects.append(tmp)

        for y in range(0, self._number_var):
            self.fields_y[y] = tk.StringVar()
            tmp = tk.Entry(textvariable=self.fields_y[y], width=10)
            tmp.grid(row=1, column=y, padx=5, pady=5)
            super()._destroyable_objects.append(tmp)

            tmp = tk.Button(text="Расчет", command=self._check_valid, width=20)
            tmp.grid(row=3, columnspan=self._number_var)
            super()._destroyable_objects.append(tmp)

    def _check_valid(self):
        self.start_x = [0.0 for _ in range(0, self._number_var)]
        self.start_y = [0.0 for _ in range(0, self._number_var)]

        for x in range(0, len(self.fields_x)):
            try:
                tmp = float(self.fields_x[x].get())
            except ValueError:
                return False
            self.start_x[x] = tmp

        for y in range(0, len(self.fields_y)):
            try:
                tmp = float(self.fields_y[y].get())
            except ValueError:
                return False
            self.start_y[y] = tmp

        self._start_calculations()
        self._build_plot()

    def _build_plot(self):
        y_p1 = [self.eval_P1(x) for x in self.start_x]
        y_p2 = [self.eval_P2(x) for x in self.start_x]
        f = Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot()
        #print(self.start_x)
        #print(y_p1)
        a.plot(self.start_x, self.start_y, "b", self.start_x, y_p1, "r", self.start_x, y_p2, "y")
        #a.scatter(self.start_x, self.start_y, c='r')
        a.spines['left'].set_position('zero')
        a.spines['bottom'].set_position('zero')
        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
        str_answ = "S1 = {0}\nS2 = {1}".format(round(self.error_first,3), round(self.error_second,3))
        a.add_artist(AnchoredText(str_answ, loc=2))
        print(self.first)
        print(self.second)
        super()._clean_frame()
        canvas = FigureCanvasTkAgg(f)
        super()._destroyable_objects.append(canvas._tkcanvas)
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _start_calculations(self):
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_xy = 0
        for x in self.start_x:
            sum_x += x
        for y in self.start_y:
            sum_y += y
        for x in self.start_x:
            sum_x2 += x ** 2
        for i in range(0, len(self.start_y)):
            sum_xy += (self.start_x[i] * self.start_y[i])

        matrix = [[sum_x2, sum_x], [sum_x, len(self.start_y)]]
        answers = [sum_xy, sum_y]

        for v in range(0, len(matrix)):
            tmp = matrix[v][v]
            for x in range(0, len(matrix[0])):
                matrix[v][x] /= tmp

            answers[v] /= tmp

            for y in range(0, len(matrix)):
                if y != v:
                    multiplier = matrix[y][v]
                    for x in range(0, len(matrix[0])):
                        matrix[y][x] -= matrix[v][x] * multiplier

                    answers[y] -= answers[v] * multiplier

        self.first = "{0}*x+{1}".format(answers[0], answers[1])

        sum_P1 = 0
        for i in range(0, len(self.start_x)):
            sum_P1 += (self.eval_P1(self.start_x[i]) - self.start_y[i]) ** 2
        self.error_first = ((1 / len(self.start_x)) * sum_P1) ** (1 / 2)

        sum_x3 = 0
        sum_x4 = 0
        sum_x2y = 0

        for x in self.start_x:
            sum_x3 += x ** 3
            sum_x4 += x ** 4

        for i in range(0, len(self.start_y)):
            sum_x2y += self.start_x[i] ** 2 * self.start_y[i]

        matrix = [[sum_x2, sum_x, len(self.start_y)], [sum_x3, sum_x2, sum_x], [sum_x4, sum_x3, sum_x2]]
        answers = [sum_y, sum_xy, sum_x2y]

        for v in range(0, len(matrix)):
            tmp = matrix[v][v]
            for x in range(0, len(matrix[0])):
                matrix[v][x] /= tmp

            answers[v] /= tmp

            for y in range(0, len(matrix)):
                if y != v:
                    multiplier = matrix[y][v]
                    for x in range(0, len(matrix[0])):
                        matrix[y][x] -= matrix[v][x] * multiplier

                    answers[y] -= answers[v] * multiplier

        self.second = "{0}*x**2+{1}*x+{2}".format(answers[0], answers[1], answers[2])

        sum_P2 = 0
        for i in range(0, len(self.start_x)):
            sum_P2 += (self.eval_P2(self.start_x[i]) - self.start_y[i]) ** 2
        self.error_second = ((1 / len(self.start_x)) * sum_P2) ** (1 / 2)
