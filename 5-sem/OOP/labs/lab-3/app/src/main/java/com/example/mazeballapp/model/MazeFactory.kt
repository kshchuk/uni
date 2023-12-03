package com.example.mazeballapp.model

import java.util.Random
import java.util.Stack


class MazeFactory(
    private val COLS: Int,
    private val ROWS: Int
    )

{
        fun createMazeByDepthFirstAlgorithm(): Array<Array<Cell?>> {
            var maze = Array(COLS) { arrayOfNulls<Cell?>(ROWS) }
            val stack = Stack<Cell?>()
            var currCell: Cell?
            var nextCell: Cell?
            for (y in 0 until COLS) {
                for (x in 0 until ROWS) {
                    maze[y][x] = Cell(x, y)
                }
            }
            currCell = maze[0][0]
            currCell!!.checked = true
            do {
                nextCell = getNeighbour(maze, currCell)
                if (nextCell != null) {
                    clearWall(currCell, nextCell)
                    stack.push(currCell)
                    currCell = nextCell
                    currCell.checked = true
                } else {
                    currCell = stack.pop()
                }
            } while (!stack.isEmpty())

            return maze
        }

        private fun getNeighbour(maze: Array<Array<Cell?>>, cell: Cell?): Cell? {
            val random = Random()
            val neighbours = ArrayList<Cell?>()
            if (cell!!.point.y > 0) {
                val cellT = maze[cell.point.y - 1][cell.point.x]
                if (!cellT!!.checked) neighbours.add(cellT)
            }
            if (cell.point.x < COLS - 1) {
                val cellR = maze[cell.point.y][cell.point.x + 1]
                if (!cellR!!.checked) neighbours.add(cellR)
            }
            if (cell.point.y < ROWS - 1) {
                val cellB = maze[cell.point.y + 1][cell.point.x]
                if (!cellB!!.checked) neighbours.add(cellB)
            }
            if (cell.point.x > 0) {
                val cellL = maze[cell.point.y][cell.point.x - 1]
                if (!cellL!!.checked) neighbours.add(cellL)
            }
            return if (neighbours.size > 0) neighbours[random.nextInt(neighbours.size)] else null
        }

        private fun clearWall(cellA: Cell?, cellB: Cell) {
            if (cellA!!.point.y == cellB.point.y && cellA.point.x == cellB.point.x + 1) {
                cellA.tWall = false
                cellB.bWall = false
            }
            if (cellA.point.y == cellB.point.y && cellA.point.x == cellB.point.x - 1) {
                cellA.bWall = false
                cellB.tWall = false
            }
            if (cellA.point.y == cellB.point.y + 1 && cellA.point.x == cellB.point.x) {
                cellA.lWall = false
                cellB.rWall = false
            }
            if (cellA.point.y == cellB.point.y - 1 && cellA.point.x == cellB.point.x) {
                cellA.rWall = false
                cellB.lWall = false
            }
        }
}