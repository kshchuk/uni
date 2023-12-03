package com.example.mazeballapp.model

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Point
import java.util.Arrays
import java.util.Random
import java.util.Stack


class GameMaze {
    private val COLS = 10
    private val ROWS = 10
    private var CELL_SIZE = 0
    private var SCORE = 0
    private lateinit var maze: Array<Array<Cell?>>
    private var ballPoint: Point? = null
    private var endPoint: Point? = null
    private var wall: Paint? = null
    private var ball: Paint? = null
    private var end: Paint? = null
    private var score: Paint? = null

    enum class DIRECTION {
        T, R, B, L
    }

    init {
        initMaze()
        SCORE = 0
        wall = Paint()
        wall!!.color = Color.BLACK
        wall!!.strokeWidth = 4f
        ball = Paint()
        ball!!.color = Color.RED
        end = Paint()
        end!!.color = Color.DKGRAY
        score = Paint()
        score!!.color = Color.BLACK
        score!!.textSize = 50f
    }

    private fun reset() {
        SCORE += 1
        initMaze()
    }

    private fun initMaze() {
        val mazeFactory = MazeFactory(COLS, ROWS)
        maze = mazeFactory.createMazeByDepthFirstAlgorithm()
        ballPoint = Point(0, 0)
        endPoint = Point(COLS - 1, ROWS - 1)
    }

    fun draw(canvas: Canvas) {
        val width = canvas.width
        val height = canvas.height

        // Set canvas in the center
        canvas.translate((width - COLS * CELL_SIZE) / 2f, (height - ROWS * CELL_SIZE) / 2f)
        CELL_SIZE = width / (COLS + 1)

        // Draw maze
        for (x in 0 until COLS) {
            for (y in 0 until ROWS) {
                val cell = maze[x][y]
                val xLeft = (x * CELL_SIZE).toFloat()
                val xRight = ((x + 1) * CELL_SIZE).toFloat()
                val yTop = (y * CELL_SIZE).toFloat()
                val yBottom = ((y + 1) * CELL_SIZE).toFloat()
                if (cell!!.tWall) canvas.drawLine(xLeft, yTop, xRight, yTop, wall!!)
                if (cell.rWall) canvas.drawLine(xRight, yTop, xRight, yBottom, wall!!)
                if (cell.bWall) canvas.drawLine(xLeft, yBottom, xRight, yBottom, wall!!)
                if (cell.lWall) canvas.drawLine(xLeft, yTop, xLeft, yBottom, wall!!)
            }
        }

        // Draw ball and end points
        val offset = CELL_SIZE / 2f
        canvas.drawCircle(
            CELL_SIZE * ballPoint!!.x + offset,
            CELL_SIZE * ballPoint!!.y + offset,
            CELL_SIZE / 2.5f,
            ball!!
        )
        canvas.drawCircle(
            CELL_SIZE * endPoint!!.x + offset, CELL_SIZE * endPoint!!.y + offset, CELL_SIZE / 2.5f,
            end!!
        )
        canvas.drawText("Score: $SCORE", 0f, -20f, score!!)
    }

    fun move(direction: DIRECTION) {
        if (direction == DIRECTION.T && ballPoint!!.y > 0 && !maze[ballPoint!!.x][ballPoint!!.y]!!.tWall) {
            ballPoint!!.y -= 1
        } else if (direction == DIRECTION.R && ballPoint!!.x < ROWS - 1 && !maze[ballPoint!!.x][ballPoint!!.y]!!.rWall) {
            ballPoint!!.x += 1
        } else if (direction == DIRECTION.B && ballPoint!!.y < COLS - 1 && !maze[ballPoint!!.x][ballPoint!!.y]!!.bWall) {
            ballPoint!!.y += 1
        } else if (direction == DIRECTION.L && ballPoint!!.x > 0 && !maze[ballPoint!!.x][ballPoint!!.y]!!.lWall) {
            ballPoint!!.x -= 1
        }
        if (ballPoint!!.x == endPoint!!.x && ballPoint!!.y == endPoint!!.y) {
            reset()
        }
    }
}