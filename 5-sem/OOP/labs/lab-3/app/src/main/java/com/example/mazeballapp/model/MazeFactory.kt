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

            // start from random cell
            val random = Random()
            currCell = maze[random.nextInt(COLS)][random.nextInt(ROWS)]
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

        fun createMazeByPrimAlgorithm(): Array<Array<Cell?>> {
            var maze = Array(COLS) { arrayOfNulls<Cell?>(ROWS) }
            val random = Random()
            var currCell: Cell?
            var nextCell: Cell?
            for (y in 0 until COLS) {
                for (x in 0 until ROWS) {
                    maze[y][x] = Cell(x, y)
                }
            }

            currCell = maze[random.nextInt(COLS)][random.nextInt(ROWS)]
            currCell!!.checked = true
            do {
                nextCell = getNeighbour(maze, currCell)
                if (nextCell != null) {
                    clearWall(currCell, nextCell)
                    currCell!!.isMazePart = true
                    nextCell.isMazePart = true
                    currCell = nextCell
                    currCell.checked = true
                } else {
                    val mazeList = ArrayList<Cell?>()
                    for (y in 0 until COLS) {
                        for (x in 0 until ROWS) {
                            if (maze[y][x]!!.isMazePart) {
                                mazeList.add(maze[y][x])
                            }
                        }
                    }
                    currCell = mazeList[random.nextInt(mazeList.size)]
                }
            } while (!isAllChecked(maze))

            return maze
        }

    private fun isAllChecked(maze: Array<Array<Cell?>>): Boolean {
        for (y in 0 until COLS) {
            for (x in 0 until ROWS) {
                if (!maze[y][x]!!.checked) return false
            }
        }
        return true
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