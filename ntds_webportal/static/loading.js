
const showLoadingSpinner = (element) => {
    console.log('hi')
    const root = document.querySelector(':root')
    const backdrop = document.createElement('div')
    const spinnerContainer = document.createElement('div')
    const spinner = document.createElement('img')
    const label = document.createElement('h1')

    backdrop.style.position = 'fixed'
    backdrop.style.display = 'flex'
    backdrop.style.justifyContent = 'center'
    backdrop.style.alignItems = 'center'
    backdrop.style.zIndex = '2'
    backdrop.style.top = '0'
    backdrop.style.left = '0'
    backdrop.style.width = '100vw'
    backdrop.style.height = '100vh'
    backdrop.style.backgroundColor = 'rgba(255, 255, 255, .8)'

    root.appendChild(backdrop)

    spinnerContainer.style.position = 'fixed'
    spinnerContainer.style.display = 'flex'
    spinnerContainer.style.flexDirection = 'column'
    spinnerContainer.style.justifyContent = 'center'
    spinnerContainer.style.alignItems = 'center'
    spinnerContainer.style.zIndex = '3'

    backdrop.appendChild(spinnerContainer)

    spinner.src = '/static/lemon.svg'
    spinner.width = 320
    spinner.height = spinner.width

    label.innerHTML = 'Loading...'

    spinnerContainer.appendChild(spinner)
    spinnerContainer.appendChild(label)


    let start = null
    let progress = null
    let speed = 25000

    const toDegrees = angle => 180 / Math.PI * angle

    const spin = timestamp => {
      if (!start) start = timestamp
      progress = timestamp - start
      state = Math.sin(toDegrees(progress / speed))
            spinner.style.transform = `rotate3d(0, 1, 0, ${state * 90 + 90}deg)`
      window.requestAnimationFrame(spin)
    }

    window.requestAnimationFrame(spin)
}

const addLoadingListener = () => {
    console.log('hello')
    document.querySelectorAll('.loading-btn').forEach(button => button.addEventListener('click', showLoadingSpinner))
//    showLoadingSpinner()
}

function ready(fn) {
  if (document.attachEvent ? document.readyState === "complete" : document.readyState !== "loading"){
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

ready(addLoadingListener)
