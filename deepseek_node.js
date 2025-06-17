import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI.DeepSeekChat",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "DeepSeekChatNode") {
            // 添加自定义小部件或UI元素
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // 添加节点描述
                this.addWidget("text", "节点信息", "", (value) => {}, { 
                    multiline: true, 
                    readonly: true,
                    getValue: () => "DeepSeek Chat API 节点\n将文本发送到DeepSeek Chat API并获取回复。\n请确保在config.json中设置了有效的API密钥。\n启用测试模式可在不消耗API额度的情况下测试节点功能。"
                });
                
                // 添加测试模式提示
                const testModeWidget = this.widgets.find(w => w.name === "test_mode");
                if (testModeWidget) {
                    const origValue = testModeWidget.value;
                    const origCallback = testModeWidget.callback;
                    
                    testModeWidget.callback = function(value) {
                        if (value && !origValue) {
                            app.ui.showMessage("已启用测试模式，节点将不会实际调用API，适合用于测试节点连接和参数设置。", "info", 5000);
                        }
                        if (origCallback) {
                            return origCallback(value);
                        }
                    };
                }
                
                return result;
            };
        }
    }
});
