// Make sure sw are supported
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('sw.js')
      .then(reg => console.log('Service Worker: Registered'))
      .catch(err => console.log(`Service Worker: Error: ${err}`));
  });
}

//const publicKey = 'BNcC4xcOp0D6pwfbeTM5WnfVxIbbQho8rxDXi5oCwBe4lXh75Rrn8lZhtaBCYBwlsmxAu8HGYYFIn8WwuWJxoKk';
//
//function urlB64ToUint8Array(base64String) {
//    const padding = '='.repeat((4 - base64String.length % 4) % 4);
//    const base64 = (base64String + padding)
//        .replace(/\-/g, '+')
//        .replace(/_/g, '/');
//
//    const rawData = window.atob(base64);
//    const outputArray = new Uint8Array(rawData.length);
//
//    for (let i = 0; i < rawData.length; ++i) {
//        outputArray[i] = rawData.charCodeAt(i);
//    }
//    return outputArray;
//}
//
//registerPushNotifications = () => {
//    navigator.serviceWorker && navigator.serviceWorker.ready.then(function(serviceWorkerRegistration) {
//        serviceWorkerRegistration.pushManager.getSubscription()
//        .then(function(subscription) {
//            // subscription will be null or a PushSubscription
//            if (subscription) {
//                console.info('Got existing', subscription);
//                var key = subscription.getKey('p256dh');
//                var auth = subscription.getKey('auth');
//                console.log(JSON.stringify(subscription))
//                window.subscription = subscription;
//                return;  // got one, yay
//            }
//
//            const applicationServerKey = urlB64ToUint8Array(publicKey);
//            serviceWorkerRegistration.pushManager.subscribe({
//                userVisibleOnly: true,
//                applicationServerKey,
//            })
//            .then(function(subscription) {
//                console.info('Newly subscribed to push!', subscription);
//                window.subscription = subscription;
//            });
//        });
//    });
//};