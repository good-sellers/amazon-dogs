import React from 'react';
import DogGallery from './components/DogGallery';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>亚马逊狗狗图片展示</h1>
        <p>来自Amazon的可爱狗狗们</p>
      </header>
      <main>
        <DogGallery />
      </main>
    </div>
  );
}

export default App; 