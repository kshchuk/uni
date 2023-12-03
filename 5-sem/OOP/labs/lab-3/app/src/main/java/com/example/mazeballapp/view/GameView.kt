package com.example.mazeballapp.view

import android.content.Context
import android.graphics.Canvas
import android.hardware.Sensor
import android.hardware.SensorManager
import android.view.View
import com.example.mazeballapp.model.GameMaze


class GameView(context: Context) : View(context) {
    private val sensorManager: SensorManager
    private val accelerometer: Sensor
    private val gameMaze: GameMaze

    init {
        sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        gameMaze = GameMaze()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        gameMaze.draw(canvas)
        invalidate()
    }

    fun registerSensor() {
// TODO
    }

    fun unregisterSensor() {
        // TODO
    }
}
