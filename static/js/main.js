// Reading Progress Bar
document.addEventListener('DOMContentLoaded', function() {
    const article = document.querySelector('article');
    const progressBar = document.querySelector('.reading-progress-bar');
    
    if (article && progressBar) {
        window.addEventListener('scroll', () => {
            const articleHeight = article.clientHeight;
            const windowHeight = window.innerHeight;
            const scrolled = window.scrollY;
            const progress = (scrolled / (articleHeight - windowHeight)) * 100;
            progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
        });
    }
});

// Newsletter Form
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = newsletterForm.querySelector('input[type="email"]').value;
            
            try {
                const response = await fetch('/newsletter/subscribe/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ email })
                });
                
                if (response.ok) {
                    showAlert('success', 'Thank you for subscribing!');
                    newsletterForm.reset();
                } else {
                    showAlert('danger', 'Subscription failed. Please try again.');
                }
            } catch (error) {
                showAlert('danger', 'An error occurred. Please try again later.');
            }
        });
    }
});

// Social Share Buttons
function shareArticle(platform) {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);
    
    let shareUrl;
    switch (platform) {
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
            break;
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
            break;
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${url}&title=${title}`;
            break;
    }
    
    window.open(shareUrl, '_blank', 'width=600,height=400');
}

// Table of Contents Generator
document.addEventListener('DOMContentLoaded', function() {
    const article = document.querySelector('article');
    const toc = document.querySelector('.table-of-contents ul');
    
    if (article && toc) {
        const headings = article.querySelectorAll('h2, h3');
        headings.forEach((heading, index) => {
            const id = `heading-${index}`;
            heading.id = id;
            
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = `#${id}`;
            a.textContent = heading.textContent;
            if (heading.tagName === 'H3') {
                li.style.paddingLeft = '1rem';
            }
            li.appendChild(a);
            toc.appendChild(li);
        });
    }
});

// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Lazy Loading Images
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    if ('loading' in HTMLImageElement.prototype) {
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback for browsers that don't support lazy loading
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
        document.body.appendChild(script);
    }
});