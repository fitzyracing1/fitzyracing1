using UnityEngine;

[DefaultExecutionOrder(-1000)]
public class EnsureCamera : MonoBehaviour
{
    void Awake()
    {
        Camera cam = Camera.main;
        if (cam == null)
        {
            GameObject camObj = new GameObject("Main Camera");
            cam = camObj.AddComponent<Camera>();
            camObj.tag = "MainCamera";
            camObj.AddComponent<AudioListener>();
            camObj.transform.position = new Vector3(0f, 2f, -5f);
            camObj.transform.rotation = Quaternion.Euler(10f, 0f, 0f);
            Debug.Log("Emergency camera created!");
        }
        else
        {
            Debug.Log("Camera already exists: " + cam.gameObject.name);
        }
    }
}
