import React, { Component } from 'react';
import '../stylesheets/Header.css';

class Header extends Component {
  navTo(uri) {
    window.location.href = window.location.origin + uri;
  }

  render() {
    return (
      <div className='App-header'>
        <h1
          onClick={() => {
            this.navTo('');
          }}
        >
          {/* Udacitrivia */}
          Trivia
        </h1>
        <ul className='nav'>
        <li
          onClick={() => {
            this.navTo('');
          }}
        >
          List
        </li>
        <li
          onClick={() => {
            this.navTo('/add');
          }}
        >
          Add
        </li>
        <li
          onClick={() => {
            this.navTo('/play');
          }}
        >
          Play
        </li>
        </ul>
        
      </div>
    );
  }
}

export default Header;
