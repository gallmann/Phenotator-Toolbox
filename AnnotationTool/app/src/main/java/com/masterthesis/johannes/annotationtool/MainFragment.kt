package com.masterthesis.johannes.annotationtool

import android.Manifest
import androidx.appcompat.app.AppCompatActivity
import android.content.Intent
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.*
import android.widget.*
import android.content.pm.PackageManager
import android.widget.LinearLayout
import android.content.Context.MODE_PRIVATE
import android.content.IntentSender
import com.google.android.material.snackbar.Snackbar
import androidx.core.content.ContextCompat
import com.google.android.gms.common.api.ResolvableApiException
import com.google.android.gms.location.*
import com.google.android.gms.tasks.Task
import java.io.File
import com.davemorrissey.labs.subscaleview.ImageViewState
import android.graphics.PointF
import com.davemorrissey.labs.subscaleview.SubsamplingScaleImageView
import java.lang.Exception


class MainFragment : Fragment(), AdapterView.OnItemClickListener, View.OnTouchListener, View.OnClickListener, SubsamplingScaleImageView.OnImageEventListener, CompoundButton.OnCheckedChangeListener {
    private lateinit var flowerListView: ListView
    private lateinit var polygonSwitch: Switch
    private lateinit var annotationState: AnnotationState
    private lateinit var imageView: MyImageView
    var restoredImageViewState: ImageViewState? = null
    private var currentEditIndex: Int = 0
    lateinit private var undoButton: MenuItem

    private var startTime: Long = 0
    private var startX: Float = 0.toFloat()
    private var startY: Float = 0.toFloat()

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private lateinit var locationCallback: LocationCallback

    private lateinit var imagePath: String

   /** FRAGMENT LIFECYCLE FUNCTIONS **/
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setHasOptionsMenu(true)
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(activity!!)
        locationCallback = object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult?) {
                locationResult ?: return
                for (location in locationResult.locations){
                    imageView.updateLocation(location)
                }
            }
        }

    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        // Inflate the layout for this fragment
        val fragmentView: View = inflater.inflate(R.layout.fragment_main, container, false)
        flowerListView = fragmentView.findViewById<ListView>(R.id.flower_list_view)
        flowerListView.onItemClickListener = this
        fragmentView.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.INVISIBLE

        fragmentView.findViewById<Button>(R.id.done_button).setOnClickListener(this)
        fragmentView.findViewById<Button>(R.id.cancel_button).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.upButton).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.downButton).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.leftButton).setOnClickListener(this)
        fragmentView.findViewById<ImageButton>(R.id.rightButton).setOnClickListener(this)
        polygonSwitch = fragmentView.findViewById<Switch>(R.id.polygonSwitch)
        polygonSwitch.setOnCheckedChangeListener(this)

        return fragmentView
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        if(savedInstanceState != null && savedInstanceState.containsKey(IMAGE_VIEW_STATE_KEY)) {
            restoredImageViewState = savedInstanceState.getSerializable(IMAGE_VIEW_STATE_KEY) as ImageViewState
        }

        val prefs = context!!.getSharedPreferences(SHARED_PREFERENCES_KEY, MODE_PRIVATE)
        val restoredText = prefs.getString(LAST_OPENED_IMAGE_URI, null)
        if (restoredText != null) {
            imagePath = restoredText
            requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE), READ_PHONE_STORAGE_RETURN_CODE_STARTUP)
        }
    }

    override fun onResume() {
        super.onResume()
        if(::annotationState.isInitialized){
            if (annotationState.hasLocationInformation()){
                stopLocationUpdates()
                startLocationUpdates()
            }
        }
    }

    override fun onPause() {
        super.onPause()
        stopLocationUpdates()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        val state = imageView.state
        if (state != null) {
            outState.putSerializable(IMAGE_VIEW_STATE_KEY, imageView.state)
        }
        imageView.recycle()
    }

    override fun onDestroyView() {
        val imageViewContainer: RelativeLayout = view!!.findViewById<RelativeLayout>(R.id.imageViewContainer)
        imageViewContainer.removeView(imageView)
        super.onDestroyView()
    }

    override fun onDestroy() {
        super.onDestroy()
        imageView.recycle()
    }


    /** OPTIONS MENU FUNCTIONS **/
    override fun onCreateOptionsMenu(menu: Menu, inflater: MenuInflater) {
        inflater.inflate(R.menu.main, menu);
        undoButton = menu.getItem(0)
        enableUndoButton(false)
        super.onCreateOptionsMenu(menu, inflater)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        when (item.itemId) {
            R.id.action_import_image ->{
                openImage()
                return false
            }
            R.id.action_undo -> {
                removeCurrentPolygonPoint()
                return false
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    fun enableUndoButton(enable: Boolean){
        undoButton.setEnabled(enable)
        if(enable){
            undoButton.getIcon().setAlpha(255);
        }
        else{
            undoButton.getIcon().setAlpha(130);
        }
    }



    /** CONTROL VIEW FUNCTIONS **/
    override fun onItemClick(p0: AdapterView<*>?, view: View, index: Int, p3: Long) {

        (flowerListView.adapter as FlowerListAdapter).selectedIndex(index)
        imageView.invalidate()
    }

    override fun onClick(view: View) {
        when(view.id){
            R.id.done_button -> {
                if(annotationState.currentFlower!!.isPolygon && annotationState.currentFlower!!.polygon.size < 3){
                    Snackbar.make(view!!, R.string.to_small_polygon, Snackbar.LENGTH_LONG).show();
                }
                else{
                    annotationState.permanentlyAddCurrentFlower()
                    updateControlView()
                    imageView.invalidate()
                }
            }
            R.id.cancel_button -> {
                annotationState.cancelCurrentFlower()
                updateControlView()
                imageView.invalidate()
            }
            R.id.upButton, R.id.downButton, R.id.leftButton, R.id.rightButton -> {
                moveCurrentMark(view.id)
            }
        }
    }

    override fun onCheckedChanged(switch: CompoundButton, checked: Boolean) {
        when(switch.id){
            R.id.polygonSwitch ->{
                annotationState.currentFlower!!.isPolygon = checked
                imageView.invalidate()
            }
        }
    }

    fun updateControlView(){
        if(annotationState.currentFlower == null){
            view!!.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.INVISIBLE
            flowerListView.adapter = null
            enableUndoButton(false)
        }
        else{
            view!!.findViewById<LinearLayout>(R.id.annotation_edit_container).visibility = View.VISIBLE
            var adapter = FlowerListAdapter(activity as AppCompatActivity,annotationState)
            flowerListView.adapter = adapter
            polygonSwitch.isChecked = annotationState.currentFlower!!.isPolygon
        }
    }


    /** IMAGE VIEW FUNCTIONS **/

    fun initImageView(){


        if(!isExternalStorageWritable() || !File(imagePath).exists()){
            Snackbar.make(view!!, R.string.could_not_load_image, Snackbar.LENGTH_LONG).show();
            val editor = context!!.getSharedPreferences(SHARED_PREFERENCES_KEY, MODE_PRIVATE).edit()
            editor.putString(LAST_OPENED_IMAGE_URI,null)
            editor.apply()
            return
        }
        println(imagePath)
        view!!.findViewById<ProgressBar>(R.id.progress_circular).visibility = View.VISIBLE
        view!!.findViewById<ProgressBar>(R.id.progress_circular).bringToFront()
        annotationState = AnnotationState(imagePath, getFlowerListFromPreferences(context!!))
        putFlowerListToPreferences(annotationState.flowerList,context!!)
        val imageViewContainer: RelativeLayout = view!!.findViewById<RelativeLayout>(R.id.imageViewContainer)



        if(::imageView.isInitialized){
            imageView.recycle()
            //imageViewContainer.removeView(imageView)
        }

        imageView = MyImageView(context!!,annotationState, stateToRestore = restoredImageViewState)
        imageView.setOnTouchListener(this)
        imageView.setOnImageEventListener(this)
        imageViewContainer.addView(imageView)

        val editor = context!!.getSharedPreferences(SHARED_PREFERENCES_KEY, MODE_PRIVATE).edit()
        editor.putString(LAST_OPENED_IMAGE_URI,imagePath)
        editor.apply()
        if(annotationState.hasLocationInformation()){
            startLocationUpdates()
        }
    }

    private fun stopLocationUpdates() {
        fusedLocationClient.removeLocationUpdates(locationCallback)
    }

    private fun startLocationUpdates(){
        if (ContextCompat.checkSelfPermission(activity!!, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), LOCATION_PERMISSION_REQUEST)
        }
        else{
            val locationRequest = LocationRequest.create()?.apply {
                interval = 6000
                fastestInterval = 3000
                priority = LocationRequest.PRIORITY_HIGH_ACCURACY
            }
            val builder = LocationSettingsRequest.Builder()
                .addLocationRequest(locationRequest!!)
            val client: SettingsClient = LocationServices.getSettingsClient(activity!!)
            val task: Task<LocationSettingsResponse> = client.checkLocationSettings(builder.build())
            task.addOnSuccessListener { locationSettingsResponse ->
                fusedLocationClient.requestLocationUpdates(locationRequest,
                    locationCallback,
                    null /* Looper */)
            }

            task.addOnFailureListener { exception ->
                if (exception is ResolvableApiException){
                    try {
                        startIntentSenderForResult(exception.getResolution().getIntentSender(), TURN_ON_LOCATION_USER_REQUEST, null, 0, 0, 0, null);
                    } catch (sendEx: IntentSender.SendIntentException) {
                    }
                }
            }



        }
    }

    private fun moveCurrentMark(id: Int){
        when(id){
            R.id.leftButton -> {
                annotationState.currentFlower!!.decrementXPos(currentEditIndex)
            }
            R.id.rightButton -> {
                annotationState.currentFlower!!.incrementXPos(currentEditIndex)
            }
            R.id.upButton -> {
                annotationState.currentFlower!!.decrementYPos(currentEditIndex)
            }
            R.id.downButton -> {
                annotationState.currentFlower!!.incrementYPos(currentEditIndex)
            }
        }
        imageView.invalidate()
    }

    private fun openImage(){
        requestPermissions(arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE), READ_PHONE_STORAGE_RETURN_CODE)
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out kotlin.String>, grantResults: IntArray): Unit {
        if(requestCode == READ_PHONE_STORAGE_RETURN_CODE){
            if (permissions[0].equals(Manifest.permission.READ_EXTERNAL_STORAGE) && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "image/*"
                }
                startActivityForResult(intent, OPEN_IMAGE_REQUEST_CODE)
            }
        }
        else if(requestCode == READ_PHONE_STORAGE_RETURN_CODE_STARTUP){
            if (grantResults.isNotEmpty() && permissions[0].equals(Manifest.permission.READ_EXTERNAL_STORAGE) && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                initImageView()
            }

        }
        else if(requestCode == LOCATION_PERMISSION_REQUEST) {
            //TODO: arrayoutofbounds exception
            if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startLocationUpdates()
            }
        }
    }

    override fun onReady() {
        view!!.findViewById<ProgressBar>(R.id.progress_circular).visibility = View.INVISIBLE
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, resultData: Intent?) {

        if (requestCode == OPEN_IMAGE_REQUEST_CODE && resultCode == AppCompatActivity.RESULT_OK) {
            resultData?.data?.also { uri ->
                imagePath = uriToPath(uri)
                restoredImageViewState = null
                initImageView()
            }
        }
        if (requestCode == TURN_ON_LOCATION_USER_REQUEST) {
            startLocationUpdates()
        }
    }

    override fun onTouch(view: View, event: MotionEvent): Boolean {

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                startX = event.x
                startY = event.y
                startTime = System.currentTimeMillis()
            }
            MotionEvent.ACTION_UP -> {
                val endX = event.x
                val endY = event.y
                val endTime = System.currentTimeMillis()
                if (isAClick(startX, endX, startY, endY, startTime, endTime, context!!)) {
                    if(imageView.isEditable()){
                        val editFlower = imageView.clickedOnExistingMark(endX,endY);
                        if(editFlower != null){
                            clickedOnExistingMark(editFlower)
                        }
                        else {
                            clickedOnNewPosition(event)
                        }
                    }
                }
            }
        }
        return false
    }

    private fun clickedOnNewPosition(event: MotionEvent){
        if(annotationState.currentFlower != null && annotationState.currentFlower!!.isPolygon){
            var sourcecoord: PointF = imageView.viewToSourceCoord(PointF(event.x, event.y))!!
            annotationState.currentFlower!!.addPolygonPoint(Coord(sourcecoord.x,sourcecoord.y))
            setCurrentEditIndex(annotationState.currentFlower!!.polygon.size-1)
            if(annotationState.currentFlower!!.polygon.size > 1) enableUndoButton(true)
            imageView.invalidate()
        }
        else{
            var sourcecoord: PointF = imageView.viewToSourceCoord(PointF(event.x, event.y))!!
            annotationState.addNewFlowerMarker(sourcecoord.x, sourcecoord.y)
            setCurrentEditIndex(0)
            updateControlView()
            imageView.invalidate()
        }
    }

    private fun clickedOnExistingMark(flower: Pair<Flower,Int>){
        if(flower.first.isPolygon){
            setCurrentEditIndex(flower.second)
            annotationState.startEditingFlower(flower.first)
            setCurrentEditIndex(flower.second)
            if(annotationState.currentFlower!!.polygon.size > 1) enableUndoButton(true)
            updateControlView()
            imageView.invalidate()
        }
        else{
            annotationState.startEditingFlower(flower.first)
            setCurrentEditIndex(0)
            updateControlView()
            imageView.invalidate()
        }
    }

    private fun removeCurrentPolygonPoint(){
        if(annotationState.currentFlower != null){
            annotationState.currentFlower!!.removePolygonPointAt(currentEditIndex)
            setCurrentEditIndex(annotationState.currentFlower!!.polygon.size-1)
            if(annotationState.currentFlower!!.polygon.size > 1) enableUndoButton(true)
            else enableUndoButton(false)
            imageView.invalidate()
        }
    }

    private fun setCurrentEditIndex(index: Int){
        currentEditIndex = index
        imageView.currentEditIndex = index
    }




    /** UNUSED STUBS **/

    override fun onImageLoaded() {}

    override fun onTileLoadError(e: Exception?) {}

    override fun onPreviewReleased() {}

    override fun onImageLoadError(e: Exception?) {}

    override fun onPreviewLoadError(e: Exception?) {}




}
