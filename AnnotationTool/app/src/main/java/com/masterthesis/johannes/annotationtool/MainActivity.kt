package com.masterthesis.johannes.annotationtool

import android.net.Uri
import android.os.Bundle
import com.google.android.material.navigation.NavigationView
import androidx.fragment.app.Fragment
import androidx.core.view.GravityCompat
import androidx.appcompat.app.ActionBarDrawerToggle
import androidx.appcompat.app.AppCompatActivity
import android.view.MenuItem
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.app_bar_main.*
import android.widget.Toast
import android.R.attr.orientation
import android.content.res.Configuration
import android.content.Context.INPUT_METHOD_SERVICE
import androidx.core.content.ContextCompat.getSystemService
import android.app.Activity
import android.content.Context
import android.widget.EditText
import android.view.MotionEvent
import android.view.inputmethod.InputMethodManager


class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {

    var mainFragment: MainFragment? = null
    var settingsFragment: SettingsFragment? = null
    var currentFragment: Fragment? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {

            mainFragment = MainFragment()

            activateFragment(R.id.nav_annotations)
        }
        else {

            for (fragment in supportFragmentManager.fragments) {
                if(fragment is MainFragment){
                    mainFragment = fragment
                }
                else if(fragment is SettingsFragment){
                    settingsFragment = fragment
                }
            }

            if(savedInstanceState.containsKey(CURRENT_FRAGMENT_KEY)) {
                activateFragment(savedInstanceState.getInt(CURRENT_FRAGMENT_KEY))
            }
        }

        setSupportActionBar(toolbar)

        val toggle = ActionBarDrawerToggle(
            this, drawer_layout, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        drawer_layout.addDrawerListener(toggle)
        toggle.syncState()

        nav_view.setNavigationItemSelectedListener(this)

    }


    private fun activateFragment(id:Int) {
        val transaction = supportFragmentManager.beginTransaction()
        when (id) {
            R.id.nav_annotations -> {
                if(mainFragment == null){
                    mainFragment = MainFragment()
                }
                transaction.replace(R.id.fragment_container, mainFragment!!, R.id.nav_annotations.toString())
                currentFragment = mainFragment
            }

            R.id.nav_settings -> {
                if(settingsFragment == null){
                    settingsFragment = SettingsFragment()
                }
                transaction.replace(R.id.fragment_container, settingsFragment!!, R.id.nav_settings.toString())
                currentFragment = settingsFragment
            }
        }

        transaction.commit()
    }

    override fun onBackPressed() {
        if (drawer_layout.isDrawerOpen(GravityCompat.START)) {
            drawer_layout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        if(currentFragment is MainFragment){
            outState.putInt(CURRENT_FRAGMENT_KEY,R.id.nav_annotations)
        }
        else if(currentFragment is SettingsFragment){
            outState.putInt(CURRENT_FRAGMENT_KEY,R.id.nav_settings)
        }
    }

    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        // Handle navigation view item clicks here.
        var newFragment: Fragment? = null


        activateFragment(item.itemId)
        drawer_layout.closeDrawer(GravityCompat.START)
        return true
    }


    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {
        val v = currentFocus

        if (v != null &&
            (ev.action == MotionEvent.ACTION_UP || ev.action == MotionEvent.ACTION_MOVE) &&
            v is EditText &&
            !v.javaClass.getName().startsWith("android.webkit.")
        ) {
            val scrcoords = IntArray(2)
            v.getLocationOnScreen(scrcoords)
            val x = ev.rawX + v.left - scrcoords[0]
            val y = ev.rawY + v.top - scrcoords[1]

            if (x < v.left || x > v.right || y < v.top || y > v.bottom) {
                hideKeyboard(this)
            }
        }
        return super.dispatchTouchEvent(ev)
    }

    fun hideKeyboard(activity: Activity?) {
        if (activity != null && activity.window != null && activity.window.decorView != null) {
            val imm = activity.getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager
            imm.hideSoftInputFromWindow(activity.window.decorView.windowToken, 0)
        }
    }

}
