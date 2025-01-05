window.onload = function () {
    // Récupérer l'élément image
    var img = document.getElementById('movie-poster');
    
    if (img) {
        img.onload = function () {
            // Récupérer les dimensions de l'image
            var imageWidth = img.width;
            var imageHeight = img.height;
            
            // Appliquer ces dimensions au body
            document.body.style.width = imageWidth + 'px';
            document.body.style.height = imageHeight + 'px';
        };
    } else {
        console.error("Image avec l'ID 'movie-poster' non trouvée.");
    }
};


window.onload = function () {
    const colorThief = new ColorThief();
    const img = document.getElementById('movie-poster');

    // Assurez-vous que l'image est complètement chargée avant d'extraire les couleurs
    if (img.complete) {
        const dominantColor = colorThief.getColor(img);
        console.log('Couleur dominante : ', dominantColor);
    } else {
        img.addEventListener('load', function () {
            const dominantColor = colorThief.getColor(img);
            console.log('Couleur dominante : ', dominantColor);
        });
    }
};
