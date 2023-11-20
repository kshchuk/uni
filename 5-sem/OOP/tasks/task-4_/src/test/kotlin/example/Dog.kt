package example

class Dog : Animal(), Mammal {
    var breed: String = "Generic Breed"
    fun bark() {
        println("Bark!")
    }
    private fun sleep() {
        println("The dog is sleeping")
    }
}