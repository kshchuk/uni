package com.example.mazeballapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import com.example.mazeballapp.view.GameView

class MainActivity : ComponentActivity() {
    var gameView: GameView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        gameView = GameView(this)
        setContentView(gameView)
    }

    override fun onResume() {
        super.onResume()
        gameView!!.registerSensor()
    }

    override fun onPause() {
        super.onPause()
        gameView!!.unregisterSensor()
    }
}