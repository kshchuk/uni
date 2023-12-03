package com.example.mazeballapp.model

import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.view.View


class GameSensorListener(var view: View, gameMaze: GameMaze) :
    SensorEventListener {
    var gameMaze: GameMaze

    init {
        this.gameMaze = gameMaze
    }

    override fun onSensorChanged(sensorEvent: SensorEvent) {
        if (sensorEvent.sensor.type == Sensor.TYPE_ACCELEROMETER) {
            val x = sensorEvent.values[0].toInt()
            val y = sensorEvent.values[1].toInt()
            if (x <= -2) {
                gameMaze.move(GameMaze.DIRECTION.R)
            } else if (x >= 2) {
                gameMaze.move(GameMaze.DIRECTION.L)
            } else if (y <= -2) {
                gameMaze.move(GameMaze.DIRECTION.T)
            } else if (y >= 2) {
                gameMaze.move(GameMaze.DIRECTION.B)
            }
            view.invalidate()
        }
    }

    override fun onAccuracyChanged(sensor: Sensor, i: Int) {}
}