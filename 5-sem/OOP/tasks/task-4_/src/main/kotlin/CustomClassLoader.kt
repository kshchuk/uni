
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException

class CustomClassLoader : ClassLoader() {
    @Throws(ClassNotFoundException::class)
    public override fun findClass(name: String): Class<*> {
        val b = loadClassFromFile(name)
        return defineClass(name, b, 0, b.size)
    }

    @Throws(ClassNotFoundException::class)
    private fun loadClassFromFile(fileName: String): ByteArray {
        var fileName = fileName
        fileName = fileName.replace('.', File.separatorChar) + ".class"
        val inputStream = javaClass.getClassLoader().getResourceAsStream(fileName)
        val buffer: ByteArray
        val byteStream = ByteArrayOutputStream()
        var nextValue = 0
        try {
            while (inputStream.read().also { nextValue = it } != -1) {
                byteStream.write(nextValue)
            }
        } catch (e: IOException) {
            throw RuntimeException(e)
        } catch (ignored: NullPointerException) {
            throw ClassNotFoundException("Class not found: $fileName")
        }
        buffer = byteStream.toByteArray()
        return buffer
    }
}