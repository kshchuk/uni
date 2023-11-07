
class test {
    fun test() {
        println("test")
    }
}

fun main(args: Array<String>) {
    val classDescription = ClassDescription()
    println(classDescription.describeClass("java.util.Random"))
}