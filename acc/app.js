
// For job creation
async function createJobPosting() {
    try {
        const response = await fetch('http://localhost:8000/api/jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                company_id: 1,
                title: "Python Developer",
                description: "Need Python expert",
                requirements: "3+ years Python",
                deadline: "2024-12-31"
            })
        });
        return await response.json();
    } catch (error) {
        console.error('Error creating job:', error);
    }
}

// For application submission
document.getElementById('applicationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('fullName').value);
    formData.append('email', document.getElementById('email').value);
    formData.append('resume', document.getElementById('resume').files[0]);
    formData.append('job_id', '1');

    try {
        const response = await fetch('http://localhost:8000/api/applications', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            alert('Application submitted successfully!');
        } else {
            throw new Error('Submission failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to submit application');
    }
});