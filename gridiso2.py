#!/usr/bin/python
version = "0.1"

from tkinter import *
from pymol import cmd, querying
import Pmw


def __init__(self):
    self.menuBar.addmenuitem(
        "Plugin",
        "command",
        "Sliders",
        label="Grid iso",
        command=lambda s=self: run_it(s),
    )


def run_it(self):
    """Collects the names of loaded map objects, starts the GUI"""
    self.objects = cmd.get_names()
    self.map_objects = []
    for i in self.objects:
        if cmd.get_type(i) == "object:map":
            self.map_objects.append(i)
            # in api.py have a look to find for example if there
            # is a way to get the min e max energy value...
            # print cmd.get_extent(i)
            # print cmd.count_states(i)

    if self.map_objects == []:
        print("No XPLOR found...")
    else:
        BigBang(self, self.map_objects)


# ===GUI stuff==============================================================>
class PieceGroup:
    """Creates a group where all pieces are created, kept and managed"""

    def __init__(self, group_name, group_container):
        self.group_name = group_name
        self.group_container = group_container
        self.piece_index = 0  # piece index is used to create different named pieces
        self.my_pieces = []  # here piece objects are kept
        # self.is_collapsed = 0  # this needs pmw version 1.2
        # ---create group--->
        self.piece_group = self.createPieceGroup()

    def createPieceGroup(self):
        self._piece_group = Pmw.Group(self.group_container, tag_text=self.group_name)
        # self._piece_group = Pmw.Group(self.group_container,tag_pyclass = Checkbutton, tag_text = self.group_name) # this needs pmw version 1.2
        # self._piece_group.configure(tag_command = self.toggleGroup) # this needs pmw version 1.2
        self._piece_group.pack(fill=X)
        return self._piece_group

    def createPiece(self, group_obj):
        self.my_pieces.append(Piece(group_obj))
        self.piece_index += 1

    # ---This needs pmw ver 1.2--->
    # def toggleGroup(self):
    #       if self.is_collapsed == 0:
    #               self.piece_group.collapse()
    #               self.is_collapsed = 1
    #       else:
    #               self.piece_group.expand()
    #               self.is_collapsed = 0


class Piece:
    """Creates, destroys and manages pieces"""

    def __init__(self, group_obj):
        self.group_obj = group_obj
        self.group_name = self.group_obj.group_name
        self.piece_name = (
            self.group_obj.group_name + "_" + str(self.group_obj.piece_index + 1)
        )
        # ---
        self.obj_color = 0  # initial color index
        self.curr_val = (
            0.0  # this variable is level of slider, also shown in label above slider
        )
        self.curr_min = -5.0  # initial min value
        self.curr_max = 5.0  # initial max value
        self.surf_types = {
            "solid": "mesh",
            "mesh": "dots",
            "dots": "solid",
        }  # this is used for changing representation
        self.curr_surf_type = self.surf_types["mesh"]  # default initial surface type
        # ---piece parts--->
        self.piece_frame = self.createPieceFrame()
        # upper part
        # self.name_label = self.createPieceLabel(self.piece_name, 0, 0)
        self.min_label = self.createPieceLabel("Min", 0, 1)
        self.max_label = self.createPieceLabel("Max", 0, 3)
        self.curr_entry = self.createPieceEntry(0, 2, 4)
        self.curr_entry.insert(0, str(self.curr_val))
        self.curr_entry.bind(
            "<Return>", self.setNewCurrVal
        )  # This is explicitly killed...
        # lower part
        self.type_button = self.createPieceButton(1, 0)  # This is explicitly killed...
        self.min_entry = self.createPieceEntry(1, 1, 4)
        self.min_entry.bind(
            "<Return>", self.setNewVal
        )  # entry field bind return event, and calls set_new_val
        self.max_entry = self.createPieceEntry(
            1, 3, 4
        )  # which updates new entered value
        self.max_entry.bind("<Return>", self.setNewVal)  #
        self.slider = self.createPieceSlider(1, 2)
        # print 'Hi from '+self.piece_name
        # ---/
        self.drawContour()

    def __del__(self):
        """Destroys widgets explicitely, actually some are destroyed elsewhere"""
        self.slider.destroy()  # this is abundant...
        self.max_entry.destroy()  # --"--
        self.min_entry.destroy()  # --"--
        self.type_button.destroy()  # --"--
        self.curr_entry.destroy()  # --"--
        self.max_label.destroy()
        self.min_label.destroy()
        self.name_label.destroy()
        self.piece_frame.destroy()
        cmd.delete(self.piece_name)
        # print 'Bye from '+self.piece_name

    # ===Piece parts===>
    def createPieceSlider(self, _row, _column):
        self._slider = Scale(
            self.piece_frame,
            from_=self.curr_min,
            to=self.curr_max,
            orien=HORIZONTAL,
            sliderlength=10,
            resolution=0.1,
            showvalue=0,
        )
        self._slider.bind("<B1-Motion>", self.sliderMoved)
        self._slider.bind("<ButtonRelease-1>", self.sliderMoved)
        self._slider.grid(row=_row, column=_column)
        return self._slider

    def createPieceButton(self, _row, _column, _width=5):
        self._button = Button(
            self.piece_frame,
            width=_width,
            text=self.curr_surf_type,
            command=self.changeType,
        )
        self._button.grid(row=_row, column=_column)
        return self._button

    def createPieceEntry(self, _row, _column, _width):
        self._entry = Entry(self.piece_frame, width=_width)
        self._entry.grid(row=_row, column=_column)
        return self._entry

    def createPieceLabel(self, _text, _row, _column, _textvariable=None):
        self._piece_label = Label(
            self.piece_frame, text=_text, textvariable=_textvariable
        )
        self._piece_label.grid(row=_row, column=_column)
        return self._piece_label

    def createPieceFrame(self):
        self._piece_frame = Frame(self.group_obj.piece_group.interior())
        self._piece_frame.pack(fill=X)
        return self._piece_frame

    # ===/

    # ===Parts managing personnel===>
    def setNewCurrVal(self, event):
        """ """
        if float(self.curr_entry.get()) <= float(self.curr_max) and float(
            self.curr_entry.get()
        ) >= float(self.curr_min):
            self.curr_val = self.curr_entry.get()
            self.curr_entry.delete(0, END)
            self.curr_entry.insert(0, self.curr_val)
            self.slider.set(self.curr_val)
            self.drawContour()
        else:
            print("Value is out of range!!!")

    def setNewVal(self, event):
        """Update min/max value"""
        # manages all new value incorporation things
        if self.min_entry.get() != "":
            if self.checkNewVal("min", self.min_entry.get()):
                self.curr_min = self.min_entry.get()
                self.min_entry.delete(0, END)  # clear the new value
            else:
                self.min_entry.delete(0, END)
                return
        elif self.max_entry.get() != "":
            if self.checkNewVal("max", self.max_entry.get()):
                self.curr_max = self.max_entry.get()
                self.max_entry.delete(0, END)  # clear the new value
            else:
                self.min_entry.delete(0, END)
                return
        self.slider.destroy()
        self.slider = self.createPieceSlider(1, 2)

    def checkNewVal(self, type_, val):
        """Checks if new value is ok"""
        try:
            self.tmp = float(val)
        except ValueError:
            print("The value is wrong, not a proper number maybe?")
            return 0
        if type_ == "min" and float(val) > float(self.curr_max):
            print("You want to set min value larger then max value?")
            return 0
        if type_ == "max" and val < self.curr_min:
            print("You want to set max value smaller then min value?")
            return 0
        return 1

    def changeType(self):
        """Changes type of contour"""
        self.curr_surf_type = self.surf_types[self.curr_surf_type]
        self.drawContour()
        self.type_button.destroy()
        self.type_button = self.createPieceButton(1, 0)

    def sliderMoved(self, event):
        """Manages changed slider value"""
        if self.curr_val != self.slider.get():
            self.curr_val = self.slider.get()
            self.curr_entry.delete(0, END)
            self.curr_entry.insert(0, str(self.curr_val))
            self.drawContour()

    def drawContour(self):
        """ """
        # ---manage surface color--->
        # DM fix 2006.02
        # added this try block because there was an exeption
        # comming from this color managment...
        # apparantly it is so because first tim get_object_color_inedex is called
        # there is not piece object yet created in the scene
        try:
            if querying.get_object_color_index(self.piece_name) == -1:
                pass
            else:
                self.obj_color = querying.get_object_color_index(self.piece_name)
        except:
            pass

        # ---draw surface of required type--->
        if self.curr_surf_type == "solid":
            cmd.isodot(self.piece_name, self.group_name, self.curr_val)
            cmd.color(str(self.obj_color), self.piece_name)
        elif self.curr_surf_type == "mesh":
            cmd.isosurface(self.piece_name, self.group_name, self.curr_val)
            cmd.color(str(self.obj_color), self.piece_name)
        elif self.curr_surf_type == "dots":
            cmd.isomesh(self.piece_name, self.group_name, self.curr_val)
            cmd.color(str(self.obj_color), self.piece_name)

    # ===/


class BigBang:
    """Creates the world..."""

    def __init__(self, master, group_list):
        master = master.root  # these are linking to pymol stuff
        self.universe = master  #
        self.group_list = group_list
        self.universe = Toplevel(master)
        # ---create universe--->
        self.group_house = self.createHouse()  # container for groups
        self.manage_house = self.createManageHouse()  # birht H.Q.
        # ---populate primary world--->
        self.world_content = []
        self.createWorld()
        # ---create world population control H.Q.--->
        # self.birth_option = self.createBirthOption()
        # self.piece_birth = self.birthButton()
        # self.death_option = self.createDeathOption()
        # self.piece_death = self.deathButton()
        # ---about Info--->
        # self.about_info = self.aboutInfo()

    # ===BigBang at work===>
    def createWorld(self):
        for i in self.group_list:
            self._piece_group = PieceGroup(i, self.group_house)
            self._piece_group.createPiece(self._piece_group)
            self.world_content.append(self._piece_group)

    def createHouse(self):
        self._house = Frame(self.universe)
        self._house.pack(fill=X)
        return self._house

    def createManageHouse(self):
        self._house = Frame(self.universe)
        self._house.pack(fill=X)
        self._house = Frame(self._house)
        self._house.pack(fill=X, side=LEFT)
        return self._house

    # ===/

    # ===Gods at work===>
    # ------Spring - delivering new pieces--->
    # def createBirthOption(self):
    #       #Creates birth option menu
    #       self._option_menu = Pmw.OptionMenu(self.manage_house, items = self.group_list, menubutton_width = 5)
    #       self._option_menu.grid(row = 0, column = 0)
    #       return self._option_menu

    # def birthButton(self):
    #       #Creates birth button
    #       self._birth = Button(self.manage_house, text = '+', padx = 3, command = self.pieceBirth)
    #       self._birth.grid(sticky = E, row = 0, column = 1)
    #       return self._birth

    def pieceBirth(self):
        # The piece birth function
        _birth_in = self.getGroupObj(self.birth_option.getvalue())
        self.world_content[_birth_in].createPiece(self.world_content[_birth_in])
        self.death_option.destroy()
        # self.death_button.destroy()
        self.death_option = self.createDeathOption()
        # self.death_button = self.createDeathButton()

    # ------Autumn - killing pieces --->
    # def createDeathOption(self):
    #       #Creates death option menu
    #       self._option_menu = Pmw.OptionMenu(self.manage_house, items = self.getPieceList(), menubutton_width = 5)
    #       self._option_menu.grid(row = 1, column = 0)
    #       return self._option_menu
    #
    # def deathButton(self):
    #       #Creates death button
    #       self._death = Button(self.manage_house, text = '-', padx = 3, command = self.pieceDeath)
    #       self._death.grid(row = 1, column = 1)
    #       return self._death

    def pieceDeath(self):
        # The piece death function
        self._dies = self.getPieceObj(self.death_option.getvalue())
        if self._dies != []:  # if there are still living pieces
            # self._dies[0].my_pieces[self._dies[1]].curr_entry.unbind("<Return>")
            self._dies[0].my_pieces[
                self._dies[1]
            ].curr_entry.destroy()  # This must be explicitly killed already here..
            self._dies[0].my_pieces[self._dies[1]].type_button.destroy()  # --"--
            self._dies[0].my_pieces[self._dies[1]].min_entry.destroy()  # --"--
            self._dies[0].my_pieces[self._dies[1]].max_entry.destroy()  # --"--
            self._dies[0].my_pieces[self._dies[1]].slider.destroy()  # --"--

            del self._dies[0].my_pieces[
                self._dies[1]
            ]  # dereferencing piece instance which leads to trash collection
            del self._dies  # and call of destructor in piece object
            self.death_option.destroy()  #
            self.death_option = self.createDeathOption()  # update of death option menu
        else:
            print("Everyone is already dead :-(")

    # ===/

    # ---Supporting personnel--->
    def aboutInfo(self):
        """Label to display about info"""
        self._about_info = Label(
            self.manage_house, text="              Ver." + version + "  by D.M."
        )
        self._about_info.grid(row=1, column=2)
        return self._about_info

    def getPieceList(self):
        """Returnds full list of pieces from all groups"""
        _piece_list = []
        for i in self.world_content:
            for ii in i.my_pieces:
                _piece_list.append(ii.piece_name)
        return _piece_list

    def getGroupObj(self, group_name):
        """Returns index of group object in self.group_list"""
        for i in self.world_content:
            if i.group_name == group_name:
                return self.world_content.index(i)
        print("There is no such group")

    def getPieceObj(self, piece_name):
        """Returns list where list[0] is group object and list[1] is index of a piece in this group"""
        for i in self.world_content:
            for ii in i.my_pieces:
                if ii.piece_name == piece_name:
                    return [i, i.my_pieces.index(ii)]
        print("There is no such piece")
        return []


# =====================================================================================================/
