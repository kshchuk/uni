package com.example.task_4

import android.os.Bundle
import androidx.activity.ComponentActivity
import ClassDescription
import android.util.Log

class MainActivity {
    public fun MainActivity() {
        val classDescription = ClassDescription()
        val description = classDescription.describeClass("String")
        Log.i("Out", description)
    }
}