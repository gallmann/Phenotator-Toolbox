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


class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener,
    MainFragment.OnFragmentInteractionListener, SettingsFragment.OnFragmentInteractionListener {

    lateinit var mainFragment: MainFragment
    lateinit var settingsFragment: SettingsFragment
    lateinit var currentFragment: Fragment

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

            setContentView(R.layout.activity_main)



        if(savedInstanceState != null) {
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
        else{
            activateFragment(R.id.nav_annotations)
        }


        setSupportActionBar(toolbar)

        val toggle = ActionBarDrawerToggle(
            this, drawer_layout, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        drawer_layout.addDrawerListener(toggle)
        toggle.syncState()

    //TODO:
        nav_view.setNavigationItemSelectedListener(this)

    }

    private fun activateFragment(id:Int){

        val transaction = supportFragmentManager.beginTransaction()
        when(id){
            R.id.nav_annotations ->{
                if(::mainFragment.isInitialized){
                }
                else{
                    mainFragment = MainFragment()
                }
                transaction.replace(R.id.fragment_container, mainFragment)
                currentFragment = mainFragment
            }

            R.id.nav_settings ->{
                if(::settingsFragment.isInitialized){
                }
                else{
                    settingsFragment = SettingsFragment()
                }
                transaction.replace(R.id.fragment_container, settingsFragment)
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

    public override fun onFragmentInteraction(uri: Uri): Unit {

    }
}
