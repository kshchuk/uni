package com.example.mazeballapp.model

import android.graphics.Point

class Cell(x: Int, y: Int)  {
    val point: Point
    var tWall = true
    var rWall = true
    var bWall = true
    var lWall = true
    var checked = false
    var isMazePart = false

    init {
        point = Point(x, y)
    }
}