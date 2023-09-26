package com.example.task_4

import android.os.Bundle
import androidx.activity.ComponentActivity
import ClassDescription
import android.util.Log

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val classDescription = ClassDescription()
        val description = classDescription.describeClass("ClassDescription")
        Log.i("Out", description)
    }
}