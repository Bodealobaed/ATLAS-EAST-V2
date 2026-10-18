"""Research-only DICOM/NIfTI preview. PHI is deliberately not shown or exported."""
import io
import numpy as np
from PIL import Image

def read_medical_image(filename, data):
    name=filename.lower()
    if name.endswith('.dcm') or name.endswith('.dicom'):
        import pydicom
        ds=pydicom.dcmread(io.BytesIO(data))
        arr=np.asarray(ds.pixel_array,dtype=np.float32)
        if arr.ndim==3: arr=arr[len(arr)//2]
        if arr.ndim!=2: raise ValueError('Unsupported DICOM image dimensions for preview.')
        meta={'modality':str(ds.get('Modality','Unknown')),'patient_age':str(ds.get('PatientAge','Not provided')),'rows':int(arr.shape[0]),'columns':int(arr.shape[1]),'source':'DICOM'}
    elif name.endswith(('.nii','.nii.gz')):
        import nibabel as nib
        import tempfile,os
        suffix='.nii.gz' if name.endswith('.nii.gz') else '.nii'
        with tempfile.NamedTemporaryFile(suffix=suffix,delete=False) as f:
            f.write(data);path=f.name
        try:
            volume=np.asarray(nib.load(path).dataobj,dtype=np.float32)
        finally: os.unlink(path)
        if volume.ndim<2: raise ValueError('NIfTI data must have at least two dimensions.')
        while volume.ndim>2: volume=np.take(volume,volume.shape[-1]//2,axis=-1)
        arr=volume
        meta={'modality':'NIfTI volume','rows':int(arr.shape[0]),'columns':int(arr.shape[1]),'source':'NIfTI'}
    elif name.endswith(('.png','.jpg','.jpeg','.tif','.tiff')):
        arr=np.asarray(Image.open(io.BytesIO(data)).convert('L'),dtype=np.float32)
        meta={'modality':'Unverified research image','rows':int(arr.shape[0]),'columns':int(arr.shape[1]),'source':'Raster image'}
    else: raise ValueError('Supported image formats: DICOM, NIfTI, PNG, JPEG, TIFF.')
    arr=np.nan_to_num(arr,nan=0,posinf=0,neginf=0)
    lo,hi=np.percentile(arr,[1,99]); hi=hi if hi>lo else lo+1
    gray=(np.clip((arr-lo)/(hi-lo),0,1)*255).astype('uint8')
    b=io.BytesIO();Image.fromarray(gray).save(b,format='PNG')
    return b.getvalue(),meta
