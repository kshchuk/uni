import java.util.Random

class test {
    fun test() {
        println("test")
    }
}

fun main(args: Array<String>) {
    val classDescription = ClassDescription()
    var rand = Random(1)
    println(classDescription.describeClass("ClassDescription"))
}