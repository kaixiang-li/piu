#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_piu
----------------------------------

Tests for `piu` module.
"""

from piu import Piu

class PiuTest():
    p = Piu("test.pdf")

    p.text()

    p.create_images(output="images", index=True)

