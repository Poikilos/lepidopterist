#!/usr/bin/env python
'''
This file is part of the SoftController project
Copyright 2021 Jake "Poikilos" Gustafson

License: MIT License (See <https://github.com/poikilos/SoftController>)
'''
import sys

_verbose_controller_stats = False
_show_controller_stats = False

def error(msg):
    sys.stderr.write(str(msg)+"\n")

def _keycode_to_str_dummy(keycode):
    return str(keycode)

def set_controllers_verbose(on):
    '''
    Enable all controller messages continuously.

    Sequential arguments:
    on -- True for on, False for off
    '''
    global _verbose_controller_stats
    _verbose_controller_stats = on

class Controller:
    '''
    Each button, axis, hat, or key is mapped to a single sid (software
    id) identifying an action in your own terms. In that way, you name
    a virtual actuator and map a real actuator (key(s), button, axis,
    hat (can affect two sids)) to it.

    A keyboard keycode can set a virtual actuator to a value specified
    on add if set to True (or 0 if set to False). Each sid is a string
    that is a key in the self._states dict. The value is any number,
    such as 0 for not pressed, 1 for pressed, or -1 for the opposite
    direction.

    The state of each virtual actuator can be affected by multiple
    types of hardware actuators and up to two keyboard keys. If 4 keys
    are necessary such as for a hat, then you must add two sids such
    as 'x' and 'y' (use the addKeyAsAxisValue twice for each sid but
    with a different keycode and value--See addKeyAsAxisValue).

    Create the controller(s) in a different file. Call all of the add
    methods on the controller before your program calls any other
    methods on the controller.
    '''

    # region initialization

    def __init__(self):
        self.deadZone = .2
        self._firstButton = 1
        self._states = {}  # The state of each virtual actuator, usually
                           # -1.0 to 1.0 (or 0 or 1 for buttons, or any
                           # number of keyboard keys can affect it)

        self._btn_to_sid = {}  # map joystick button [str(num)] to sid
        self._sid_to_btn = {}  # reverse: [str(sid)] = button [str(num)]

        self._kc_to_sid = {}  # map keyboard [keycode] to sid
        self._sid_to_kcs = {}  # reverse map: [sid] to multiple keycodes
        self._kc_value = {}  # make the keycode set a specific value

        self._ax_to_sid = {}  # map joystick [axisIndex] to sid
        self._sid_to_ax = {}  # reverse map: [str(axis)] sid
        self._axes = {}  # real hardware values for change tracking

        self._hat_to_sids = {}  # hat [hatID] values to sids: (sid, sid)
        self._sid_to_hat = {}  # reverse map: either axis sid to hatID
        self._inversions = {}  # hat [hatID]: if value is True invert y


    def format(self, message, enable_game_controller,
               keycode_to_str=None, add_key_str=True,
               add_btn_str=False, opening="", closing=""):
        '''
        Use the mappings from this softcontroller.Controller instance to
        fill in [bracketed] sids in the message, otherwise merely
        remove the brackets.

        The default _firstButton is 1 (see button_name_if).

        Sequential arguments:
        message -- Format and return this string.
        enable_game_controller -- For succinct code, return a key if
                                  this is False. For example, pass
                                  controls.gamepad_used() as the value.
        keycode_to_str -- Optionally provide a callback method to use to
                          convert a keycode to a key name string, such
                          as pygame.key.name (call pygame.init() first
                          or you'll get "unknown key").
        add_key_str -- Suffix " key" or " keys" after the result when
                       the result is a key.
        add_btn_str -- Prefix "button " before the result when the
                       result is a button.
        opening -- Prefix it with this if present.
                   Set it to None for '(' only on buttons, "" for
                   never.
        closing -- Suffix it with this if present.
                   Set it to None for ')' only on buttons, "" for
                   never.
        '''
        if keycode_to_str is None:
            keycode_to_str = _keycode_to_str_dummy
        keystr = keycode_to_str
        btnOpening = opening
        btnClosing = closing
        if btnOpening is None:
            btnOpening = ')'
            opening = ""
        if btnClosing is None:
            btnClosing = ')'
            closing = ""
        while True:
            oBI = message.find('[')  # opening bracket index
            cBI = -1
            if oBI >= 0:
                cBI = message.find(']', oBI)  # closing bracket index
            if (cBI < 0):
                return message
            sid = message[oBI+1:cBI]
            btnName = self.button_name_if(
                sid,
                enable_game_controller,
                opening=btnOpening,
                closing=btnClosing,
                add_btn_str=add_btn_str,
            )
            if btnName is None:
                keycodes = self._sid_to_kcs.get(sid)
                keycode = None
                if keycodes is not None:
                    if len(keycodes) == 1:
                        keycode = keycodes[0]
                if keycode is not None:
                    btnName = keystr(keycode)
                    if 'unknown' in btnName:
                        error("Unknown keycode: {}"
                              " (make sure you call pygame.init first"
                              " if keycode_to_str is pygame.key.name)"
                              "".format(keycodes))
                    if add_key_str:
                        btnName += " key"
                elif keycodes is not None:
                    btnName = '/'.join(keystr(i) for i in keycodes)
                    if 'unknown' in btnName:
                        error("Unknown keycodes: {}"
                              " (make sure you call pygame.init first"
                              " if keycode_to_str is pygame.key.name)"
                              "".format('/'.join(str(i) for i in keycodes)))
                    if add_key_str:
                        btnName += " keys"
                else:
                    error("Warning: there are no keycodes for '{}'"
                          " in {}".format(sid, self._sid_to_kcs))
                if btnName is not None:
                    if opening is not None:
                        btnName = opening + btnName
                    if closing is not None:
                        btnName += closing
            if btnName is not None:
                message = message.replace('[' + sid + ']', btnName)
            else:
                message = message.replace('[' + sid + ']', sid)

    def button_name_if(self, sid, enable, opening="(", closing=")",
                       add_btn_str=True):
        '''
        The default _firstButton is 1 (button 0 is named "1" and that
        is what is returned; If the controller's buttons are labeled
        starting at 0, set _firstButton to 0 first).

        Sequential arguments:
        sid -- Use this mapped virtual actuator from this controller.
        enable -- For succinct code, return None if this is False.
                  For example, pass controls.gamepad_used() as the value.
        opening -- Prefix the result with this.
        closing -- Suffix the result with this.
        add_btn_str -- Prefix the result with this (after opening).

        Returns:
        an actuator type (axis, button, or hat) then a space then the index,
        all enclosed by opening&closing, otherwise None if enable is False
        or the sid is not mapped to anything on this controller.
        '''
        if opening is None:
            opening = ""
        if closing is None:
            closing = ""
        name = None
        if not enable:
            return None
        typeStr = None
        index = self._sid_to_btn.get(sid)
        if index is not None:
            if add_btn_str:
                typeStr = "button"
            else:
                typeStr = None
        else:
            index = self._sid_to_ax.get(sid)
            if index is not None:
                typeStr = "axis"
            else:
                # print("{} is not a button.".format(sid))
                index = self._sid_to_hat.get(sid)
                if index is not None:
                    typeStr = "hat"

        if index is not None:
            typeStrPrefix = ""
            indexStr = str(index + self._firstButton)
            if typeStr is not None:
                typeStrPrefix = typeStr + " "
            name = opening + typeStrPrefix + indexStr + closing
        return name

    def _raiseIfSidValueBad(self, sid):
        msg = ("in {} '<' or '>' in sid are not allowed since they are"
               " used as comparison operators when passed within the"
               " sid argument of getBool.".format(sid))
        if '<' in sid:
            raise ValueError(msg)
        elif '>' in sid:
            raise ValueError(msg)

    def addKeyAsAxisValue(self, keycode, sid, value):
        '''
        keycode -- Set the keycode value.
        sid -- Choose a new/existing virtual actuator.
        value -- Set the axis to this value (such as: Make a down
                 arrow key set the axis value to 1)
        '''
        self._raiseIfSidValueBad(sid)
        try:
            tmp = sid.strip()
        except AttributeError:
            raise TypeError("The sid must be some kid of string")
        self._kc_to_sid[str(keycode)] = sid
        if self._sid_to_kcs.get(sid) is None:
            self._sid_to_kcs[sid] = []
        self._sid_to_kcs[sid].append(keycode)
        self._kc_value[str(keycode)] = value
        self._states[sid] = 0

    def addAxis(self, axisIndex, sid):
        '''
        Sequential arguments:
        axisIndex -- an actual joystick axis number
        sid -- Choose a new/existing virtual actuator.
        '''
        self._raiseIfSidValueBad(sid)
        try:
            tmp = sid.strip()
        except AttributeError:
            raise TypeError("The sid must be some kid of string")
        self._ax_to_sid[str(axisIndex)] = sid
        self._sid_to_ax[sid] = axisIndex
        self._states[sid] = 0

    def addButton(self, button, sid):
        '''
        Sequential arguments:
        button -- an actual joystick button number
        sid -- Choose a new/existing virtual actuator.
        '''
        self._raiseIfSidValueBad(sid)
        try:
            tmp = sid.strip()
        except AttributeError:
            raise TypeError("The sid must be some kid of string")
        self._btn_to_sid[str(button)] = sid
        self._sid_to_btn[sid] = button
        self._states[sid] = 0

    def addKey(self, keycode, sid):
        '''
        This only sets a boolean value. For arrow keys: instead of
        calling this method, call addKeyAsAxisValue twice with the
        same sid but a different keycode and value (such as -1 and 1).

        Sequential arguments:
        keycode -- a hardware keycode
        sid -- Choose a new/existing virtual actuator.
        '''
        self._raiseIfSidValueBad(sid)
        self._kc_to_sid[str(keycode)] = sid
        if self._sid_to_kcs.get(sid) is None:
            self._sid_to_kcs[sid] = []
        self._sid_to_kcs[sid].append(keycode)
        self._states[sid] = 0

    # endregion initialization

    # region runtime

    def getTrues(self):
        results = []
        for sid, v in self._states.items():
            if self.getBool(sid):
                results.append(sid)
        return results

    def getBool(self, sid):
        '''
        Get the value as True if > 0, otherwise False.

        Sequential arguments:
        sid -- Choose an existing virtual actuator. If it contains '>'
               or '<' then the comparison operator will be used:
               - You must place the sid on the left side of the operator
                 if you use one.
        '''
        this_show_stats = _show_controller_stats
        if _verbose_controller_stats:
            this_show_stats = True

        got = None
        result = None
        old = None
        if '<' in sid:
            old = sid
            sid, r_operand = sid.split('<')
            got = self._states.get(sid)
            if got is None:
                raise KeyError("{} is not a registered controller sid"
                               "(operation: {}). _states: {}"
                               "".format(sid, old, self._states))
            result = int(got < float(r_operand))
        elif '>' in sid:
            old = sid
            sid, r_operand = sid.split('>')
            got = self._states.get(sid)
            if got is None:
                raise KeyError("{} is not a registered controller sid"
                               "(operation: {}). _states: {}"
                               "".format(sid, old, self._states))
            result = int(got > float(r_operand))

        else:
            got = self._states.get(sid)
            result = got
        if this_show_stats:
            if old is not None:
                # print("{} was sid"
                #       "(operation: {}). result: {}"
                #       "".format(sid, old, (result > 0)))
                pass

        if got is None:
            raise KeyError("{} is not a registered controller sid"
                           ". _states: {}".format(sid, self._states))
        return result > 0

    def getRaw(self, sid):
        '''
        Sequential arguments:
        sid -- Choose an existing virtual actuator.
        '''
        got = self._states.get(sid)
        if got is None:
            raise KeyError("{} is not a registered controller sid"
                           "".format(sid))
        # NOTE: Use _inversions on set, not here on get, since multiple
        #       physical actuators can affect a virtual one.
        return got

    def getInt(self, sid):
        '''
        Get the value as -1, 0, or 1 (It will be 0 unless
        abs(self._states[sid]) > self.deadZone).

        Sequential arguments:
        sid -- Choose an existing virtual actuator.
        '''
        this_show_stats = _show_controller_stats
        if _verbose_controller_stats:
            this_show_stats = True
        got = self._states.get(sid)
        if got is None:
            raise KeyError("{} is not a registered controller sid"
                           "".format(sid))
        # NOTE: Use _inversions on set, not here on get, since multiple
        #       physical actuators can affect a virtual one.
        if abs(got) > self.deadZone:
            if got > 0:
                return 1
            else:
                return -1
        return 0

    def toKeys(self):
        '''
        Get a list of keys where the index is the keycode and the
        value is True or False for whether it is pressed. This only
        works for keys mapped using addKey and set using setKey.
        '''
        pressed = []
        count = 0
        for sid, kcs in self._sid_to_kcs.items():
            for kc in kcs:
                if (kc + 1) > count:
                    count = kc + 1
        for kc in range(count):
            keyValue = self._kc_value.get(str(kc))
            if keyValue is None:
                keyValue = 1
            sid = self._kc_to_sid.get(str(kc))
            if sid is None:
                pressed.append(False)
                continue
            stateValue = self._states[sid]
            if abs(stateValue) > self.deadZone:
                # Determine which key affected the the sid
                # since the key may set the sid to a certain
                # value such as left and right arrows both affecting
                # a sid called 'x':
                if (keyValue > 0) and (stateValue > 0):
                    pressed.append(True)
                elif (keyValue < 0) and (stateValue < 0):
                    pressed.append(True)
                else:
                    pressed.append(False)
            else:
                pressed.append(False)
        return pressed

    def setKey(self, keycode, on):
        '''
        Sequential arguments:
        keycode -- a hardware keycode such as pygame.key.* constants
        on -- True for pressed, False for released. If the key was
              defined using addKeyAsAxisValue, then a True value
              becomes the value you set at that time.
        '''
        value = 0
        if on:
            value = self._kc_value.get(str(keycode))
            if value is None:
                value = int(on)
        sid = self._kc_to_sid.get(str(keycode))
        if sid is None:
            error("Warning: sid is None for keycode {}".format(keycode))
            return False
        self._states[sid] = value
        return True

    def isPastDeadZone(self, value):
        if value is None:
            # Maybe someone did _axes.get(unmappedAxisIndex)--that's ok:
            # The value is stored by setAxis anyway if it was called
            # even if the axisIndex is not mapped.
            return False
        return abs(value) > self.deadZone

    def _getHWAxis(self, axis):
        '''
        Get a cached value of the hardware axis (not mapped!) such as
        for comparison with a not yet set value. Since this is not
        mapped, only use this method if you know you want the value from
        a specific axis index.

        Sequential arguments:
        axis -- the unmapped hardware axis index

        Returns:
        The cached value of the axis from the last setAxis call that
        used the same axis index, otherwise None.
        '''
        return self._axes.get(str(axis))


    def setAxis(self, axis, value):
        '''
        Set the value at the sid that you defined by addAxis
        (However, not set a value unless abs(value) > self.deadZone).

        Sequential arguments:
        axis -- The axis number must already be mapped using
                addAxis so this method knows which sid to affect.
        value -- The raw value is usually -1.0 to 1.0 but it doesn't
                 matter. You can get it later with any "get" method
                 that gets a single value.

        returns:
        1 if movement goes past the deadzone, 0 if not but the axis is
        mapped, otherwise -1 if not mapped at all (The axis will not set
        anything at all if it is not mapped to some sid)
        '''
        this_show_stats = _show_controller_stats
        if _verbose_controller_stats:
            this_show_stats = True
        self._axes[str(axis)] = value
        # ^ Save the hardware value even if the index is not mapped.
        sid = self._ax_to_sid.get(str(axis))
        if sid is None:
            return -1
        if self.isPastDeadZone(value):
            try:
                tmp = float(value)
            except ValueError:
                print("The value for axis {} should be a number"
                      " but is {}."
                      "".format(axis, value))
            self._states[sid] = value
            if this_show_stats:
                print("joystick axis {} = {}"
                      "".format(axis, value))
            return 1
        else:
            self._states[sid] = 0
        return 0  # present but not actuated

    def setButton(self, button, on):
        '''
        Sequential arguments:
        button -- Set a hardware gamepad button number such as from a
                  pygame joystick. It must be already mapped using
                  addButton so that this method knows what virtual
                  actuator sid to affect.
        on -- True for pressed, False for released (converted to 0 or 1
              if True or False, otherwise the integer is preserved but
              other values are not supported)

        Returns:
        True if mapped, otherwise False (The button won't set
        anything if it isn't mapped)
        '''
        this_show_stats = _show_controller_stats
        if _verbose_controller_stats:
            this_show_stats = True

        sid = self._btn_to_sid.get(str(button))
        if this_show_stats:
            print("set {} to {} via button {}"
                  "".format(sid, on, button))
        if sid is None:
            return False
        self._states[sid] = int(on)
        return True

    def setHat(self, hat, values):
        '''
        Set a hat such as a d-pad (any hardware actuator with two axes).

        Sequential arguments:
        hat -- Specify the hat index from the hardware controller. This
               hat must already be mapped using addHat in order for this
               method to know which virtual actuator sid to affect.
        values -- The tuple containing the values of the hat, usually
                  two coordinates, each of which can be -1, 0, or 1.
                  Only a two-long tuple is supported.

        True if mapped, otherwise False (The hat won't set
        anything if it isn't mapped)
        '''
        if len(values) != 2:
            raise ValueError("The hat values argument must be a tuple"
                             " or list that has two elements.")
        sids = self._hat_to_sids.get(str(hat))
        if sids is None:
            return False
        sid0, sid1 = sids
        self._states[sid0] = values[0]
        multiplier = 1
        if self._inversions.get(sid1) is True:
            multiplier = -1
        self._states[sid1] = values[1] * multiplier
        return True

    def addHat(self, hat, sids, invert_y):
        '''
        Sequential arguments:
        hat -- Specify the hat index from the hardware controller.
        sids -- Specify a tuple containing two sids to affect since a
                hat (such as a d-pad) has two values, usually
                interpreted as x and y.
        invert_y -- if True, multiply y value by -1
        '''
        if len(sids) != 2:
            raise ValueError("The hat sids argument must be a tuple"
                             " or list that has two elements.")
        self._hat_to_sids[str(hat)] = (sids[0], sids[1])
        self._sid_to_hat[sids[0]] = hat
        self._sid_to_hat[sids[1]] = hat
        # ^ Both sids point to the same hat.
        self._inversions[sids[1]] = invert_y

    def clearPressed(self):
        for sid in self._states.keys():
            self._states[sid] = 0
        for k in self._axes.keys():
            self._axes[k] = 0.0


# endregion runtime


