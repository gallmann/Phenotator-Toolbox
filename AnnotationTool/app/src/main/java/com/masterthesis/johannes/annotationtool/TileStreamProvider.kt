package com.masterthesis.johannes.annotationtool

import android.content.Context
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import com.moagrius.tileview.io.StreamProvider
import java.io.InputStream

class TileStreamProvider(val projectDirectory: Uri, val context: Context, val metadata: Metadata) : StreamProvider {

    lateinit var templateUriString:String
    var levelRegex: Regex = "_level([0-9]|[0-9][0-9]|[0-9][0-9][0-9]|[0-9][0-9][0-9][0-9])_x".toRegex()
    var xRegex: Regex = "_x([0-9]|[0-9][0-9]|[0-9][0-9][0-9]|[0-9][0-9][0-9][0-9])_y".toRegex()
    var yRegex: Regex = "_y([0-9]|[0-9][0-9]|[0-9][0-9][0-9]|[0-9][0-9][0-9][0-9])\\.".toRegex()
    var levelFolderRegex: Regex = "%2F([0-9]|[0-9][0-9])%2Ftile".toRegex()


    init {
        templateUriString = getTemplateUriString(projectDirectory,context)
    }

    fun getTemplateUriString(projectDirectory: Uri,context: Context):String{
        val documentFile = DocumentFile.fromTreeUri(context, projectDirectory)
        for (file in documentFile!!.listFiles().reversed()) {
            if (file.isDirectory){
                for (tile in file.listFiles()){
                    return tile.uri.toString()
                }
            }
        }
        return ""
    }


    override fun getStream(column: Int, row: Int, context: Context, level: Any): InputStream {

        var tileString = templateUriString
        tileString = levelRegex.replace(tileString,"_level" + level.toString().toInt() + "_x")
        tileString = levelFolderRegex.replace(tileString,"%2F" + level + "%2Ftile")
        tileString = xRegex.replace(tileString,"_x" + column + "_y")
        tileString = yRegex.replace(tileString,"_y" + row + ".")
        return context.contentResolver.openInputStream(Uri.parse(tileString))
    }




}
