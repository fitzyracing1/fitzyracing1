using UnityEngine;

public class SimpleInput : MonoBehaviour
{
    public static SimpleInput Instance { get; private set; }

    public float horizontal;
    public float vertical;
    public bool jump;
    public bool interact;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void Update()
    {
        // Reset inputs
        jump = false;
        interact = false;

        // Try to read input - use reflection to avoid compile errors
        try
        {
            var inputType = typeof(UnityEngine.Input);
            
            // Movement
            horizontal = 0f;
            vertical = 0f;
            
            var getKey = inputType.GetMethod("GetKey", new[] { typeof(KeyCode) });
            var getKeyDown = inputType.GetMethod("GetKeyDown", new[] { typeof(KeyCode) });
            
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.W })) vertical = 1f;
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.S })) vertical = -1f;
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.A })) horizontal = -1f;
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.D })) horizontal = 1f;
            
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.UpArrow })) vertical = 1f;
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.DownArrow })) vertical = -1f;
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.LeftArrow })) horizontal = -1f;
            if ((bool)getKey.Invoke(null, new object[] { KeyCode.RightArrow })) horizontal = 1f;
            
            // Actions
            if ((bool)getKeyDown.Invoke(null, new object[] { KeyCode.Space })) jump = true;
            if ((bool)getKeyDown.Invoke(null, new object[] { KeyCode.E })) interact = true;
        }
        catch
        {
            Debug.LogWarning("Input system error - inputs disabled");
        }
    }

    public static float GetHorizontal()
    {
        return Instance != null ? Instance.horizontal : 0f;
    }

    public static float GetVertical()
    {
        return Instance != null ? Instance.vertical : 0f;
    }

    public static bool GetJump()
    {
        return Instance != null ? Instance.jump : false;
    }

    public static bool GetInteract()
    {
        return Instance != null ? Instance.interact : false;
    }
}
