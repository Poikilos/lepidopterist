#!/usr/bin/env python3
'''
This file is part of the SoftController project
Copyright 2021 Jake "Poikilos" Gustafson

License: MIT License (See <https://github.com/poikilos/SoftController>)
'''

from pygame.locals import *

verbose = False
def set_verbose(on):
    global verbose
    verbose = on

shown_already_up = {}

def set_if(d, keys, index, value, good_return=True, bad_return=False,
           default_key=None):
    '''
    if len(keys) > index and keys[index] is not None then set
    d[keys[index]] = value

    Keyword arguments:
    default_key -- Use this key (overrides the normal behavior and
                   always sets key to value) if not None.

    Returns:
    returns good_return if succeeded, bad_return if there is no match.
    '''
    if default_key is not None:
        d[default_key] = value
        return good_return
    if index < 0:
        if verbose:
            print("[set_if] The operation will be skipped since"
                  " the index is {}".format(index))
        return bad_return
    if keys is None:
        if verbose:
            print("[set_if] They keys list was None.")
        return bad_return
    if (len(keys) > index) and (keys[index] is not None):
        d[keys[index]] = value
        return good_return
    elif verbose:
        print("[set_if] There was no key set for index {}"
              " in the key list (length:{})"
              "".format(index, len(keys)))
    return bad_return


def read_event(thisController, event, pcRect=None, mb_sids=None,
               always_collide_mb=None, x_sid='x'):
               #ignore_y_for_collision=False):
    '''
    Update the controller using the event.
    'x' must be a registered sid in thisController.

    Sequential arguments:
    thisController -- Write to this controller.
    event -- Read from this event.
    pcRect --  Based on the center of this rect, set x_sid to -1 or 1.
               Otherwise always set event to mb_sids[event.button-1]
               (which must not be None if pcRect is None, otherwise
               MOUSEBUTTONDOWN is ignored).
    mb_sids -- This tuple or list becomes the mouse buttons starting
               at 1 (Pygame buttons start at 1, so mb_sids[0]
               is for button 1 which is left click, and [2] is for
               3 which is right click.
               - [0] Use the mouse result to set
                 thisController._states[mb_sids[0]]
                 and x_sid to 0 if it is in pcRect only if [0] is
                 not None (must not be None if pcRect is None,
                 otherwise MOUSEBUTTONDOWN is ignored).
               - The other elements behave the same except [1] is
                 the middle click sid, [2] is the right-click sid,
                 and so on.
               - IF NOT IN THE RECT: x_sid is used.
               - IF NO RECT: mb_sids[event.button-1] is used.
    always_collide_mb -- Always collide when this mouse button (or
                         tuple or list of multiple buttons) is
                         pressed (for example, conditionally set this to
                         right-click if you want right-click to always
                         double-jump rather than move when you are
                         already in the air). The dir will still be
                         set if outside of pcRect (that behavior won't
                         change).
    # always_dir_mb -- If this mouse button (such as 3 for
    #                  right-click) is pressed, always check for
    #                  direction even if in pcRect.
    x_sid -- Save the outside-of-rect left-right direction to this sid.
    # deprecated:
    # ignore_y_for_collision -- consider it an outside-of-rect click if
    #                          outside of the left and right bounds of
    #                          pcRect without checking the upper and
    #                          lower bounds.

    # deprecated:
    # force_click_sid -- Force the sid to this one instead of checking
    #                    mb_sids.

    Returns:
    1 controller changed, 2 if hat down, 3 if button down, 0 if not
    changed (neither up nor down)
    '''
    enable_mouse_buttons = True
    if (mb_sids is None) or (len(mb_sids)<1) or all(v is None for v in mb_sids):
        if pcRect is None:
            enable_mouse_buttons = False
            # ^ This is ok since there are no mb_sids
            if verbose and (event.type == MOUSEBUTTONDOWN):
                print("[read_event] enable_mouse_buttons is False:")
                if mb_sids is None:
                    print("[read_event]   mb_sids is None")
                else:
                    if len(mb_sids) < 1:
                        print("[read_event]   len(mb_sids)<1")
                    if all(v is None for v in mb_sids):
                        print("[read_event]   "
                              "all(v is None for v in mb_sids)")
    global _gamepad_used
    global _last_read_actuator_info
    _last_read_actuator_info = {}
    if event.type == KEYDOWN:
        thisController.setKey(event.key, True)
        _last_read_actuator_info['event.type'] = "KEYDOWN"
        _last_read_actuator_info['event.key'] = event.key
        return 3
    elif event.type == KEYUP:
        _last_read_actuator_info['event.type'] = "KEYUP"
        _last_read_actuator_info['event.key'] = event.key
        thisController.setKey(event.key, False)
        return 1
    elif event.type == JOYBUTTONDOWN:
        _last_read_actuator_info['event.type'] = "JOYBUTTONDOWN"
        _last_read_actuator_info['event.button'] = event.button
        thisController.setButton(event.button, True)
        _gamepad_used = True
        return 3
    elif event.type == JOYBUTTONUP:
        _last_read_actuator_info['event.type'] = "JOYBUTTONUP"
        _last_read_actuator_info['event.button'] = event.button
        thisController.setButton(event.button, False)
        return 1
    elif event.type == JOYHATMOTION:
        # NOTE: joy is deprecated. Use instanceid
        # (See <https://www.pygame.org/docs/ref/event.html>):
        # joyI = event.instanceid
        _last_read_actuator_info['event.type'] = "JOYHATMOTION"
        _last_read_actuator_info['event.hat'] = event.hat
        _last_read_actuator_info['event.value'] = event.value
        thisController.setHat(event.hat, event.value)
        if (event.value[0] != 0) or (event.value[1] != 0):
            _gamepad_used = True
            return 2
        return 1
    elif event.type == JOYAXISMOTION:
        _last_read_actuator_info['event.type'] = "JOYAXISMOTION"
        _last_read_actuator_info['event.axis'] = event.axis
        _last_read_actuator_info['event.value'] = event.value
        prevValue = thisController._getHWAxis(event.axis)
        prevOut = thisController.isPastDeadZone(prevValue)
        moved = thisController.setAxis(event.axis, event.value)
        nowValue = thisController._getHWAxis(event.axis)
        nowOut = thisController.isPastDeadZone(nowValue)
        if nowOut:
            _gamepad_used = True
        if prevOut is not nowOut:
            print("axis {} changed to {}".format(event.axis, nowOut))
        # else:
        #     print("axis {} was already {} at {} (raw:{})".format(event.axis, nowOut, nowValue, event.value))

        if moved > 0:
            # The axis moved out of the deadZone.
            if prevOut is not nowOut:
                # only return a change if moved and wasn't moved before
                return 2
            else:
                return 1
        elif moved < 0:
            # The axis isn't mapped.
            return 0
        else:
            # The movement isn't past the deadZone.
            return 0
    elif event.type == MOUSEBUTTONDOWN:
        shown_already_up[str(event.button)] = False
        if verbose:
            print("")
            print("[read_event] MOUSEBUTTONDOWN:")
        if not enable_mouse_buttons:
            if verbose:
                print("[read_event] enable_mouse_buttons is False")
            return 0
        result = 0
        e_x, e_y = event.pos
        # ^ the mouse
        thisController.clear_mb(event.button)
        touchText = "."
        touchEffectPos = event.pos
        # 1: left
        # 2: middle
        # 3: right
        # 4: scroll up
        # 5: scroll down
        collide = False
        value = 1
        direction = 0
        if pcRect is not None:
            collide = pcRect.collidepoint(e_x, e_y)
            if not collide:
                if e_x < pcRect.center[0]:
                    direction = -1
                else:
                    direction = 1
                if verbose:
                    print("[read_event] non-collide direction={}"
                          "".format(direction))
            elif verbose:
                print("[read_event] pcRect collide was True")
        elif verbose:
            print("[read_event] pcRect was None")
        # ^ Do real collidepoint BEFORE always_collide_mb
        #   so that non-collide situations always set the direction
        #   even though always_collide_mb will also set another button
        #   if mb_sids[event.button-1] is not None:
        if always_collide_mb is not None:
            try:
                tmpLen = len(always_collide_mb)
                for tmp in always_collide_mb:
                    if event.button == tmp:
                        if verbose:
                            print("[read_event] forced collide"
                                  " for button {} since in {}"
                                  "".format(event.button,
                                            always_collide_mb))
                        collide = True
            except TypeError:
                # It is not enumerable, so there is only one button.
                if event.button == always_collide_mb:
                    if verbose:
                        print("[read_event] forced collide for button {}"
                              "".format(event.button))
                    collide = True

        if collide:
            result = set_if(
                thisController._states,
                mb_sids,
                event.button-1,
                value,
                good_return = 2,
                bad_return = 0,
                # default_key=force_click_sid,
            )
            if result > 0:
                thisController.push_mb_sid(
                    event.button,
                    mb_sids[event.button-1],
                )
                print("[read_event collide] peek_mb_sid...")
                sid = thisController.peek_mb_sid(event.button)
                if verbose:
                    print("[read_event] button {} affected '{}'"
                          " ({})".format(
                            event.button,
                            sid,
                            thisController._last_mb_to_sids[str(event.button)]
                          ))
            elif verbose:
                print("[read_event] button {} didn't affect any sid."
                      "".format(event.button))

        if direction != 0:
            result = 2
            thisController._states[x_sid] = direction
            thisController.push_mb_sid(event.button, x_sid)
            if verbose:
                print("[read_event] button {} set '{}' to {} here."
                      "".format(event.button, x_sid, direction))
                print("[read_event] - button {} stack: "
                      " ({})".format(
                        event.button,
                        thisController._last_mb_to_sids[str(event.button)]
                      ))

        return result
    elif event.type == MOUSEBUTTONUP:
        if verbose:
            print("")
            print("[read_event] MOUSEBUTTONUP:")
        if not enable_mouse_buttons:
            return 0
        result = 1
        count = 0
        while True:
            sid = thisController.pop_mb_sid(event.button, warn=count>0)
            # ^ This mouse button was in range when down.
            if sid is None:
                result = 0
                break
            if thisController._states[sid] != 0:
                result = 1
                if verbose:
                    print("[read_event] MOUSEBUTTONUP sid {}"
                          " set to 0."
                          "".format(sid))
                thisController._states[sid] = 0
            elif thisController._states[sid] is not None:
                # thisController._states[sid] = None
                # ^ Do not set to None, or will cause KeyError
                #   accessing _states[sid]!
                if verbose and (shown_already_up.get(str(event.button)) is not True):
                    shown_already_up[str(event.button)] = True
                    print("[read_event] MOUSEBUTTONUP sid {}"
                          " was already 0."
                          "".format(sid))
                result = 0
            count += 1
            if count > 99:
                print("Error: MOUSEBUTTONUP infinite loop detected")
                break
        if verbose:
            print("[read_event] {} sid(s) were found for {}."
                  "".format(count, event.button))

        return result
    return 0
