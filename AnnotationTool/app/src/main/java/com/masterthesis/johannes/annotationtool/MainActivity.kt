package com.masterthesis.johannes.annotationtool

import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.support.design.widget.Snackbar
import android.support.design.widget.NavigationView
import android.support.v4.app.Fragment
import android.support.v4.view.GravityCompat
import android.support.v7.app.ActionBarDrawerToggle
import android.support.v7.app.AppCompatActivity
import android.view.Menu
import android.view.MenuItem
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.app_bar_main.*

class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener,
    MainFragment.OnFragmentInteractionListener, SettingsFragment.OnFragmentInteractionListener {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if(savedInstanceState == null){
            setContentView(R.layout.activity_main)


            val fragmentManager = supportFragmentManager
            val fragmentTransaction = fragmentManager.beginTransaction()

            val fragment = MainFragment()
            fragmentTransaction.add(R.id.fragment_container, fragment)
            fragmentTransaction.commit()


            setSupportActionBar(toolbar)

            val toggle = ActionBarDrawerToggle(
                this, drawer_layout, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close
            )
            drawer_layout.addDrawerListener(toggle)
            toggle.syncState()

            nav_view.setNavigationItemSelectedListener(this)
        }

    }

    override fun onBackPressed() {
        if (drawer_layout.isDrawerOpen(GravityCompat.START)) {
            drawer_layout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }


    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        // Handle navigation view item clicks here.
        var newFragment: Fragment = MainFragment()

        when (item.itemId) {
            R.id.nav_camera -> {
                newFragment = MainFragment()
            }
            R.id.nav_gallery -> {
                newFragment = SettingsFragment()
            }
            R.id.nav_slideshow -> {

            }
            R.id.nav_manage -> {

            }
            R.id.nav_share -> {

            }
            R.id.nav_send -> {

            }


        }

        val transaction = supportFragmentManager.beginTransaction()
        transaction.replace(R.id.fragment_container, newFragment)
        transaction.addToBackStack(null)
        transaction.commit()

        drawer_layout.closeDrawer(GravityCompat.START)
        return true
    }




    public override fun onFragmentInteraction(uri: Uri): Unit {

    }
}
