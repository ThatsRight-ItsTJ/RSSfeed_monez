document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const hash = urlParams.get('hash');
    
    if (hash) {
        searchByHash(hash);
    }
    
    document.getElementById('contentLockerBackground').style.display = 'block';
    document.getElementById('contentLocker').style.display = 'block';
});

async function searchByHash(hash) {
    const contentDisplay = document.getElementById('contentInfo');
    const toolTitle = document.getElementById('tool-title');
    
    try {
        const response = await fetch(`/.netlify/functions/search?hash=${encodeURIComponent(hash)}`, {
            headers: {
                'X-API-Key': import.meta.env.VITE_OFFERS_API_KEY
            }
        });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch content');
        }
        
        toolTitle.textContent = `${data.content_class} Locked`;
        
        contentDisplay.innerHTML = `
            <div class="space-y-4">
                <h3 class="text-lg font-semibold">${escapeHtml(data.title)}</h3>
                ${data.image_url ? `<img src="${escapeHtml(data.image_url)}" alt="Content thumbnail" class="w-full rounded-lg">` : ''}
                <p class="text-gray-600">${escapeHtml(data.description)}</p>
                <div class="mt-4">
                    <button onclick="unlockContent('${escapeHtml(data.redirect_url)}')" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                        Unlock Content
                    </button>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error:', error);
        contentDisplay.innerHTML = '<p class="text-red-500">Content not found or no longer available.</p>';
    }
}

function unlockContent(redirectUrl) {
    window.location.href = redirectUrl;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}