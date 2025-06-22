# **Building Agentic Model Context Protocol Servers with FastAPI and PydanticAI**

## **1\. Introduction: Bridging the Gap with Agentic MCP Servers**

The digital landscape is witnessing an accelerating demand for applications imbued with artificial intelligence, capable of engaging with the real world and executing intricate tasks with minimal human intervention.1 

This growing need has brought forth the concept of agentic workflows, where autonomous AI entities interact and make decisions to achieve specific goals. To facilitate seamless communication and interaction between these intelligent agents and the diverse array of external services they require, standardized protocols have become paramount.

The Model Context Protocol (MCP) has emerged as a significant initiative in this direction, establishing a uniform framework that enables AI applications, including sophisticated programmatic agents, to connect and utilize external tools and services through a common interface.2 

The fundamental objective of MCP is to foster interoperability within the AI ecosystem, allowing a wide spectrum of AI clients and servers to communicate effectively without the necessity for bespoke integrations.2 

This standardized protocol envisions a future where an AI agent could, for instance, leverage a web search service implemented as an MCP server to conduct in-depth research, or where a code editor could connect to a logging service via MCP to gain contextual insights during debugging.2 

Several reference implementations of basic MCP servers already exist, providing access to services such as Slack, Google Drive, GitHub, and various databases.3

A significant advancement in the evolution of MCP servers lies in the integration of internal agentic capabilities. By embedding intelligent agents directly within the server architecture, the server gains the ability to manage its operations and interactions with clients in a more dynamic and intelligent manner. 

This approach offers numerous advantages, including the capacity to handle client requests with greater flexibility, manage internal resources more effectively, and automate the invocation of necessary tools based on the specific context of a request. This integration transforms a traditional, passive server into an active, reasoning entity capable of more sophisticated interactions.  
In the pursuit of building such intelligent MCP servers, the combination of FastAPI and PydanticAI presents a compelling solution. FastAPI, a modern, high-performance web framework for Python, is exceptionally well-suited for constructing the network infrastructure required for an MCP server.4 

Its design philosophy emphasizes ease of use and developer productivity, making it an ideal choice for building robust and scalable web applications. Complementing FastAPI is PydanticAI, a Python agent framework specifically designed to bring the intuitive and type-safe development experience of FastAPI to the realm of Generative AI applications.2 

Both frameworks share a common foundation in Pydantic, a powerful data validation and serialization library, which ensures a seamless and efficient integration between the web serving layer and the agentic intelligence layer.5 This synergy provides a robust and developer-friendly platform for creating MCP servers with sophisticated internal reasoning and action capabilities.  
This report will delve into the intricacies of utilizing FastAPI and PydanticAI to construct MCP servers enhanced with internal agentic functionalities. 

It will explore the core strengths of each framework, detail the mechanisms for their integration, and examine how this powerful combination can be used to implement the various primitives of the Model Context Protocol. Furthermore, the report will discuss how PydanticAI agents can be designed to manage and interact with these primitives, how function calling capabilities can be leveraged within an MCP server, and how these agents can reason about the context provided through MCP. Finally, it will explore potential use cases for such agentic MCP servers and consider the overall developer experience of working with both FastAPI and PydanticAI in this context.

## **2\. FastAPI: The Foundation for Robust MCP Servers**

FastAPI has emerged as a leading web framework in the Python ecosystem, particularly well-suited for building modern, high-performance APIs. Its design and feature set make it an excellent foundation for developing robust MCP servers capable of handling the demands of intelligent agent interactions.

FastAPI's core strengths are numerous and directly address the requirements of server development. Built upon the ASGI (Asynchronous Server Gateway Interface) standard, leveraging Starlette for its web functionalities and Uvicorn as its high-speed ASGI server, FastAPI delivers exceptional performance and speed.4 This is crucial for an MCP server that might need to handle a high volume of requests and potentially long-running AI agent operations. 

The framework boasts an intuitive and easy-to-use API design, promoting developer productivity by simplifying the process of defining routes, handling requests, and managing responses.4 A key feature of FastAPI is its seamless integration with Pydantic, which enables automatic data validation and serialization based on Python type hints.4 This ensures that data exchanged with MCP clients is structured, validated, and conforms to the expected schemas, which is fundamental for reliable communication within the protocol.

Furthermore, FastAPI provides built-in support for asynchronous programming using Python's async and await keywords.4 This capability is particularly vital for an MCP server that integrates AI agents, as agent operations can often be computationally intensive and time-consuming. By leveraging asynchronous tasks, the server can handle concurrent client requests efficiently and offload long-running agent processes without blocking the main request-response cycle, ensuring responsiveness and scalability. 

Another significant advantage of FastAPI is its automatic generation of interactive API documentation using OpenAPI and JSON Schema standards, accessible through Swagger UI and ReDoc.4 This feature significantly enhances discoverability and testing for MCP clients, as they can readily understand the server's available endpoints, request and response structures, and parameters. 

Additionally, FastAPI incorporates a powerful dependency injection system, which improves code organization, modularity, and testability by allowing developers to easily manage and provide dependencies to different parts of the application.21 This is particularly beneficial when integrating PydanticAI agents and their required resources within the MCP server. 

The modern design and comprehensive feature set of FastAPI make it an ideal foundation for building the network infrastructure necessary to support the intelligent functionalities of an agentic MCP server. Its asynchronous capabilities are especially important for managing the potentially extended processing times associated with AI agents.

Defining the API endpoints for an MCP server is straightforward with FastAPI's routing system. Developers can use route decorators such as @app.get, @app.post, @app.put, and @app.delete to associate specific URL paths and HTTP methods with Python functions that will handle incoming client requests.17 These routes can be meticulously designed to map directly to the functionalities defined by the MCP specification, such as listing available tools, invoking specific tools, or accessing managed resources. 

For instance, an endpoint for listing available tools might be defined using @app.get("/tools"), while an endpoint for invoking a tool could use @app.post("/tools/{tool\_name}"). The exchange of data through these routes, including request and response bodies, can be effectively managed using Pydantic models.18 By defining Pydantic models that represent the expected structure of the data, developers can ensure that the MCP server receives and sends information in a well-defined and validated format, adhering to the protocol's requirements for structured data exchange. 

This combination of FastAPI routes and Pydantic models provides a clear and organized way to expose the capabilities of the MCP server to clients while maintaining data integrity and type safety.

Given that AI agent operations within an MCP server can be computationally intensive, FastAPI's BackgroundTasks feature offers a crucial mechanism for maintaining server responsiveness.6 This functionality allows developers to offload long-running tasks, such as the execution of PydanticAI agents or their individual components, to be processed in the background without blocking the main request-response cycle. 

When an MCP client makes a request that triggers an agent operation that might take some time to complete, the FastAPI route handler can initiate this operation as a background task. This enables the server to immediately return a response to the client, indicating that the request has been received and is being processed, while the agent continues its work in the background. 

Pydantic models can be used to define the structure of the data that is passed to and returned from these background tasks, ensuring that even asynchronous operations benefit from data validation and type safety.19 This approach is essential for maintaining the performance and scalability of an agentic MCP server, especially when dealing with complex client requests that require significant processing by the internal AI agents.

Furthermore, FastAPI's automatic generation of OpenAPI documentation serves as a valuable asset for MCP client developers.4 This documentation, which is automatically updated as the FastAPI application's routes and Pydantic models are defined, provides a comprehensive specification of the MCP server's API. It details all the available endpoints, the HTTP methods they support, the expected request and response schemas (defined by Pydantic models), and any required parameters. 

This readily accessible and interactive documentation allows MCP client developers to easily understand how to interact with the server, what data to send, and what format to expect in the responses. By providing this clear and up-to-date API specification, FastAPI simplifies the integration process for MCP clients and promotes a better understanding of the server's capabilities. This automatic documentation feature significantly reduces the overhead of manually creating and maintaining API documentation, making it easier for both server and client developers to work together effectively.

## **3\. PydanticAI: Empowering MCP Servers with Agentic Intelligence**

PydanticAI is a Python framework specifically engineered to facilitate the development of production-grade applications leveraging Generative AI. Built by the creators of the widely adopted Pydantic library, PydanticAI aims to bring the user-friendly and type-safe design principles of FastAPI to the domain of AI agent development.2 It provides a comprehensive set of tools and abstractions that simplify the process of building and managing AI agents within various application contexts, including MCP servers.

At its core, PydanticAI offers a rich set of functionalities that are essential for building intelligent agentic systems. One of its fundamental capabilities is the ability to define AI models using Pydantic.1 By leveraging Pydantic's declarative syntax and type hinting, developers can easily define the structure of inputs, outputs, and any intermediate data that the language models will process. This ensures that the data handled by the AI agents is well-defined, validated, and type-safe. 

Furthermore, PydanticAI boasts model-agnostic LLM integration, providing a unified interface for interacting with various leading language model providers, including OpenAI, Anthropic, Gemini, and others.7 This flexibility allows developers to choose the most suitable LLM for their specific requirements without being locked into a particular vendor or having to rewrite significant portions of their code. 

PydanticAI also enhances prompt engineering by leveraging Pydantic's validation power to dynamically generate prompts based on structured and verified inputs.11 This ensures that all data passed to the LLM is contextually accurate and complete, minimizing errors and ambiguities in communication.

A critical aspect of building reliable AI applications is ensuring the consistency and predictability of the LLM's output. PydanticAI addresses this through structured response validation, which guarantees that LLM responses conform to predefined schemas defined using Pydantic models.7 This feature is particularly valuable for MCP servers, as it ensures that the data returned to clients adheres to the expected format. Beyond processing natural language, PydanticAI empowers AI agents with function calling capabilities.14 This allows agents to invoke external functions or tools during the generation process to retrieve additional information or perform specific actions, significantly extending their capabilities beyond their inherent training data. 

PydanticAI also provides a robust framework for the creation of autonomous AI agents.5 Developers can define agents with specific roles, responsibilities, and access to tools, enabling the construction of complex and collaborative AI systems within an MCP server. To further enhance the development process, PydanticAI offers a dependency injection system.5 This allows for the seamless provision of data and services to various components of the agent, such as system prompts, tools, and result validators, improving modularity, testability, and maintainability. 

Finally, PydanticAI integrates seamlessly with Pydantic Logfire 5, a powerful tool for real-time debugging, performance monitoring, and behavior tracking of LLM-powered applications, which is crucial for ensuring the reliability and efficiency of agentic MCP servers.

Within an MCP server, PydanticAI facilitates the definition of specialized agent roles and responsibilities.22 For instance, one agent could be designed to handle the initial parsing and interpretation of client requests, while another agent might be responsible for invoking specific tools based on the request's intent. In more complex scenarios, multi-agent setups can be employed, where multiple agents collaborate and share outputs to achieve a common goal.11 This modular approach to agent design can lead to a more organized and maintainable MCP server architecture, where each agent focuses on a specific set of tasks.

Furthermore, PydanticAI's strong foundation in Pydantic allows for the effective representation of MCP data structures using Pydantic models.1 MCP primitives such as prompts, resources, and tool specifications can be defined as Pydantic models, ensuring that they are structured, validated, and type-safe. This is crucial for maintaining data integrity and facilitating the reliable exchange of information between the MCP server and its clients. By leveraging Pydantic's data validation capabilities, developers can ensure that the MCP server adheres to the protocol's specifications and handles data correctly throughout its operations.

## **4\. Integrating PydanticAI within FastAPI for Agentic MCP Servers**

The true power of this approach lies in the seamless integration of PydanticAI's agentic capabilities within the robust framework of FastAPI. This integration allows developers to build MCP servers that not only adhere to the protocol but also possess internal intelligence to handle requests and manage resources effectively.

One of the primary ways to integrate PydanticAI within a FastAPI application is by using PydanticAI agents directly within FastAPI route handlers.4 When an MCP client sends a request to a specific endpoint on the FastAPI server, the corresponding route function can instantiate a PydanticAI agent to process this request. The data from the incoming request can be passed to the agent's run method, which will then use the configured LLM, system prompts, and tools to generate a response. 

This response from the agent can then be returned as the API response to the MCP client. PydanticAI supports both synchronous (run\_sync) and asynchronous (run) execution of agents.32 FastAPI, with its support for asynchronous programming, can seamlessly handle both types of agent execution within its routes. For requests that require immediate responses, synchronous agent execution might be suitable, while for more time-consuming operations, asynchronous execution can prevent blocking and maintain server responsiveness.

For MCP requests that might involve longer processing times by the AI agent, FastAPI's background tasks provide an excellent mechanism for non-blocking execution.6 Instead of waiting for the agent to complete its operation within the route handler, the task can be offloaded to a background task. This allows the FastAPI server to immediately acknowledge the client's request, while the PydanticAI agent continues to process it in the background. Pydantic models can be used to define the data that is passed to the background task and the structure of any results that might need to be communicated back to the client (perhaps through a separate mechanism or a subsequent request).19 This approach is particularly useful for MCP operations that trigger complex reasoning or multiple tool calls by the AI agent, ensuring that the server remains responsive to other client requests.

Maintaining agent state and context across multiple MCP client requests is often crucial for providing a coherent and personalized experience. FastAPI offers various mechanisms for managing application state, such as dependencies and request state, which can be leveraged to maintain the state of PydanticAI agents or ongoing conversations.32 For conversational interactions, the message history from previous turns can be passed to the agent's run method to provide it with the necessary context for generating relevant responses in subsequent requests.32 This allows the agentic MCP server to remember past interactions and engage in more natural and meaningful dialogues with clients.

FastAPI's dependency injection system can also be effectively used to provide dependencies, such as database connections or API clients, to PydanticAI agents and their tools within the MCP server.5 By defining dependencies as part of the FastAPI application, these resources can be automatically injected into the agent's system prompts, tools, or result validators when they are executed. This not only simplifies the management of external resources required by the agents but also enhances the testability and modularity of the agent implementation within the FastAPI application by decoupling the agent's logic from the specific implementations of its dependencies.

## **5\. Implementing MCP Primitives with FastAPI and PydanticAI**

The Model Context Protocol defines several key primitives that facilitate the interaction between AI clients and servers. FastAPI, in conjunction with PydanticAI, provides the necessary tools to effectively implement and manage these primitives within an agentic MCP server.

MCP prompts, which serve as instructions or queries from the client to the server, can be represented using Pydantic models.1 By defining the structure of a prompt as a Pydantic model, the MCP server can ensure that it receives well-structured and validated input from clients. Furthermore, PydanticAI's prompt engineering capabilities can be utilized to dynamically generate prompts based on the specifics of the client request and the current context within the server.11 This allows the server to tailor its instructions to the internal AI agents based on the information received from the client.

MCP resources, which are data or information managed by the server, can also be represented using Pydantic models.1 These models can define the structure and metadata of various types of resources, such as documents, data records, or configuration settings. FastAPI endpoints can then be created to provide access to these resources based on requests from MCP clients and the internal logic of the PydanticAI agents. For example, an agent might decide which resources are relevant to a client's query and then use FastAPI to retrieve and return that information.

MCP tools, which are functions or capabilities offered by the server, can be effectively implemented using PydanticAI's function calling feature.14 The specification of an MCP tool, including its name, description, and parameters, can be mapped to a PydanticAI function tool using the @agent.tool decorator. The input and output schemas of these tools can be defined using Pydantic models, ensuring that the data exchanged with the tools is validated and type-safe. The PydanticAI agents within the MCP server can then invoke these tools based on client requests and their own reasoning capabilities, allowing them to perform actions or retrieve information as required by the MCP protocol.

## **6\. Leveraging PydanticAI's Function Calling for MCP Interactions**

PydanticAI's function calling capabilities are particularly valuable for implementing the interaction mechanisms within an MCP server. This feature allows the server to expose its internal functionalities as tools that can be invoked by its own intelligent agents, as well as respond to tool invocation requests from MCP clients.

Server-side functionalities within the FastAPI MCP server can be readily exposed as MCP tools using PydanticAI's @agent.tool decorator.14 Any Python function within the server, whether it's for accessing databases, calling external APIs, manipulating resources, or performing specific computations, can be wrapped with this decorator. This makes the function available as a callable tool to the server's internal PydanticAI agents. 

The input parameters and the return type of the function are automatically used by PydanticAI to define the tool's schema, ensuring that the agent can understand how to use it. This allows the agentic MCP server to extend its capabilities by seamlessly integrating with other services and data sources.

When an MCP client sends a request to invoke a specific tool offered by the server, the FastAPI server can map this request to the corresponding PydanticAI function tool. The server's internal agent, which has been configured with access to this tool, can then execute it, potentially based on its reasoning about the client's request and the context of the interaction. The result of the tool execution can then be returned to the client as part of the MCP response. This provides a structured and intelligent way for the MCP server to handle tool invocation requests from clients, leveraging the reasoning abilities of its internal agents to determine when and how to use the available tools.

The capabilities of an agentic MCP server can be further enhanced by utilizing the pre-built tools available within PydanticAI.27 These tools, such as those for performing web searches using DuckDuckGo or Tavily, can be readily integrated into the server's agents. This provides the server with immediate access to valuable external information and functionalities without the need for custom implementations. 

For instance, an agent within the MCP server could use a web search tool to gather information relevant to a client's query before formulating a response.

In more advanced scenarios, it might be beneficial to dynamically register tools with the PydanticAI agent within the MCP server.28 This could be based on the server's configuration, the specific client making the request, or other runtime conditions. Dynamic tool registration provides flexibility in the tools that are available to the agent at any given time, allowing the server to adapt its capabilities based on its environment or the specific needs of the clients it is serving.

## **7\. Designing Intelligent Agents for MCP Contextual Reasoning**

The intelligence of an agentic MCP server heavily relies on the design of the PydanticAI agents that power it. These agents need to be capable of understanding the context provided through the MCP, managing resources effectively, and utilizing available tools to respond appropriately to client requests.

Effective system prompts are crucial for guiding the behavior of PydanticAI agents within the MCP server.5 These prompts provide the initial instructions to the LLM, informing it how to interpret the MCP context, how to manage any resources under its purview, and how to utilize the various tools at its disposal. By carefully crafting these system prompts, developers can ensure that the agents reason about client requests in the desired manner and formulate appropriate responses based on the available information and tools.

To enable agents to maintain context across multiple interactions with an MCP client, it is essential to provide them with the history of the conversation.32 PydanticAI allows for the passing of message history to the agent's run method, enabling the agent to reason about previous turns in the conversation and provide more relevant and coherent responses. This conversational awareness is key to building intelligent MCP servers that can engage in meaningful multi-turn dialogues with clients.

The reasoning capabilities of the agents can be significantly enhanced by integrating external knowledge and resources.5 This can be achieved through PydanticAI's dependency injection mechanism or by providing access to external data sources via function calls. 

By allowing agents to retrieve and reason about information from knowledge bases, databases, or external APIs relevant to the MCP server's domain, the server can provide more informed and comprehensive responses to client requests.

Furthermore, specific reasoning logic can be embedded within the Python functions that are exposed as PydanticAI tools.14 This allows the main agent to delegate complex decision-making or information retrieval steps to these specialized tools. 

For example, a tool might contain the logic to query a specific database and process the results before returning them to the agent. This modular approach to reasoning can make the agent's overall behavior more manageable and easier to understand and update.

## **8\. Potential Use Cases and Benefits**

The combination of FastAPI and PydanticAI for building agentic MCP servers opens up a wide range of potential use cases, offering significant benefits across various domains.

One compelling application is in building intelligent data retrieval systems.1 An MCP server equipped with PydanticAI agents could intelligently retrieve data from diverse sources based on natural language queries from clients. 

The agents could understand the intent behind the query, identify the relevant data sources, and invoke the necessary tools to fetch and format the information, providing users with easier and more efficient access to the data they need through conversational interfaces.

Another significant use case lies in the creation of automated workflow execution platforms.1 An MCP server could host PydanticAI agents capable of orchestrating complex workflows by interacting with various tools and services based on client requests and their own reasoning. This could automate repetitive tasks and streamline business processes, leading to increased efficiency and productivity.

Agentic MCP servers can also power dynamic content generation services.1 Based on client specifications, internal PydanticAI agents could understand the requirements and invoke appropriate generation tools to dynamically create content such as text, code, or images. This capability enables personalized and on-demand content creation, catering to specific user needs.

Furthermore, these servers can serve as the backend for intelligent assistants and chatbots.1 By integrating PydanticAI agents and tools, an MCP server can understand user requests, access relevant information, and perform actions on behalf of the user, providing more interactive and helpful user experiences.

Finally, agentic MCP servers can be utilized to build personalized recommendation systems.1 PydanticAI agents could analyze user data, access and process relevant information through various tools, and generate tailored recommendations, enhancing user engagement and satisfaction.

Table 1: Potential Use Cases and Benefits of Agentic MCP Servers

| Use Case                        | Description                                                                                                                | Benefits                                                                        |
| :------------------------------ | :------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| Intelligent Data Retrieval      | Retrieve data from various sources based on natural language queries using AI agents.                                      | Easier and more efficient information access through conversational interfaces. |
| Automated Workflow Execution    | Orchestrate complex workflows by invoking tools and services based on AI agent reasoning.                                  | Automates repetitive tasks and streamlines business processes.                  |
| Dynamic Content Generation      | Generate text, code, or images based on client specifications using AI agents and generation tools.                        | Enables personalized and on-demand content creation.                            |
| Intelligent Assistants/Chatbots | Understand user requests, access information, and perform actions through integrated AI agents and tools.                  | Provides more interactive and helpful user experiences.                         |
| Personalized Recommendation     | Analyze user data and generate tailored recommendations by accessing and processing information using AI agents and tools. | Enhances user engagement and satisfaction through relevant suggestions.         |

9\. Developer Experience and Integration Ease

A significant advantage of using FastAPI and PydanticAI together is the positive developer experience they offer, particularly in terms of defining models, creating agents, and integrating them into a web server context.

Pydantic's declarative syntax and reliance on Python type hinting make the process of defining data models intuitive and straightforward for developers.1 This simplicity extends to defining the structure of MCP primitives and the inputs and outputs of AI agents. Furthermore, Pydantic's automatic data validation and serialization capabilities reduce the amount of boilerplate code developers need to write and ensure data integrity throughout the application lifecycle.1  
Creating AI agents with PydanticAI is also a streamlined process.5 The framework provides an intuitive API for configuring agents, including specifying the underlying LLM, setting up system prompts, defining available tools, and specifying the expected result types. The use of decorators, such as @agent.tool and @agent.system\_prompt, simplifies the definition of agent components, making the code more readable and maintainable.14

The integration between FastAPI and PydanticAI is particularly seamless due to their shared foundation in Pydantic.5 This common dependency allows for the easy use of PydanticAI models and agents within FastAPI route handlers and background tasks.4 The type safety provided by Pydantic ensures that data can be passed between the web server layer and the AI agent layer with confidence.

Beyond these core features, both frameworks offer developer-friendly tooling. FastAPI's automatic API documentation and dependency injection enhance the development experience by simplifying API understanding and resource management.4 PydanticAI's integration with Pydantic Logfire provides valuable insights into the behavior of AI agents, making debugging and monitoring more efficient.5 These features contribute to a more productive and less error-prone development process for building agentic MCP servers.

## **10\. Conclusion and Future Directions**

In conclusion, the combination of FastAPI and PydanticAI offers a powerful and developer-friendly approach to building agentic Model Context Protocol (MCP) servers. FastAPI provides the high-performance, asynchronous web framework necessary for handling MCP communication, while PydanticAI brings robust agentic capabilities, including model-agnostic LLM integration, structured response validation, function calling, and a sophisticated framework for creating and managing AI agents. Their shared foundation in Pydantic ensures seamless integration and a consistent development experience.

The benefits of this approach are numerous. The resulting MCP servers are performant and scalable, capable of handling concurrent requests and long-running AI operations. The ease of use and intuitive APIs of both frameworks enhance developer productivity, allowing for rapid development and iteration. The strong type safety and data validation provided by Pydantic contribute to the robustness and reliability of the applications.

Looking ahead, the integration of web frameworks and AI agent frameworks is likely to see further advancements. Future research could focus on enhancing agent reasoning capabilities, developing more sophisticated tool management mechanisms within the MCP context, and improving the security and scalability of agentic server-side applications. The Model Context Protocol itself is also an evolving standard, and its continued development will likely unlock new possibilities for interoperable AI systems.

The synergy between FastAPI and PydanticAI represents a significant step towards building the next generation of intelligent and interconnected applications. By leveraging the strengths of both frameworks, developers can create sophisticated agentic MCP servers that pave the way for more autonomous and context-aware AI interactions across a wide range of use cases.

#### **Works cited**

1. Build Production-Grade LLM-Powered Applications with PydanticAI \- Analytics Vidhya, accessed April 2, 2025, [https://www.analyticsvidhya.com/blog/2024/12/pydanticai/](https://www.analyticsvidhya.com/blog/2024/12/pydanticai/)  
2. Model Context Protocol (MCP) \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/mcp/](https://ai.pydantic.dev/mcp/)  
3. How to use MCP tools with a PydanticAI Agent | by Finn Andersen | Mar, 2025 | Medium, accessed April 2, 2025, [https://medium.com/@finndersen/how-to-use-mcp-tools-with-a-pydanticai-agent-0d3a09c93a51](https://medium.com/@finndersen/how-to-use-mcp-tools-with-a-pydanticai-agent-0d3a09c93a51)  
4. Integrating Pydantic with FastAPI for Efficient APIs \- Instructor, accessed April 2, 2025, [https://python.useinstructor.com/concepts/fastapi/](https://python.useinstructor.com/concepts/fastapi/)  
5. pydantic-ai/README.md at main \- GitHub, accessed April 2, 2025, [https://github.com/pydantic/pydantic-ai/blob/main/README.md](https://github.com/pydantic/pydantic-ai/blob/main/README.md)  
6. Day 43 of 100 Days Agentic Engineer Challenge: AI Agent and FastAPI \- Damian Dąbrowski, accessed April 2, 2025, [https://damiandabrowski.medium.com/day-43-of-100-days-agentic-engineer-challenge-ai-agent-and-fastapi-2920d91e1ab6](https://damiandabrowski.medium.com/day-43-of-100-days-agentic-engineer-challenge-ai-agent-and-fastapi-2920d91e1ab6)  
7. PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/](https://ai.pydantic.dev/)  
8. pydantic/pydantic-ai: Agent Framework / shim to use Pydantic with LLMs \- GitHub, accessed April 2, 2025, [https://github.com/pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)  
9. CC AI Review of Pydantic's AI Framework \- Game Changer\!\!, accessed April 2, 2025, [https://ccwithai.github.io/AI/blog/review-of-pydantics-ai-framework-d2e8f/](https://ccwithai.github.io/AI/blog/review-of-pydantics-ai-framework-d2e8f/)  
10. PydanticAI: Advancing Generative AI Agent Development through Intelligent Framework Design \- MarkTechPost, accessed April 2, 2025, [https://www.marktechpost.com/2025/03/25/pydanticai-advancing-generative-ai-agent-development-through-intelligent-framework-design/](https://www.marktechpost.com/2025/03/25/pydanticai-advancing-generative-ai-agent-development-through-intelligent-framework-design/)  
11. PydanticAI: The Next-Generation AI Agent Framework for LLMs \- Technovera, accessed April 2, 2025, [https://www.technovera.com/it-blogs/pydanticai-the-next-generation-ai-agent-framework-for-llms/](https://www.technovera.com/it-blogs/pydanticai-the-next-generation-ai-agent-framework-for-llms/)  
12. PydanticAI \- Introduction, accessed April 2, 2025, [https://docs.together.ai/docs/pydanticai](https://docs.together.ai/docs/pydanticai)  
13. PydanticAI — The NEW Agent Builder and Framework | by Shravan Kumar \- Medium, accessed April 2, 2025, [https://medium.com/@shravankoninti/pydanticai-the-new-agent-builder-and-framework-2b0852e15eb0](https://medium.com/@shravankoninti/pydanticai-the-new-agent-builder-and-framework-2b0852e15eb0)  
14. PydanticAI: A Comprehensive Guide to Building Production-Ready AI Applications, accessed April 2, 2025, [https://dev.to/yashddesai/pydanticai-a-comprehensive-guide-to-building-production-ready-ai-applications-20me](https://dev.to/yashddesai/pydanticai-a-comprehensive-guide-to-building-production-ready-ai-applications-20me)  
15. Simplify AI Agent Development with PydanticAI: A Game-Changer for Python Developers, accessed April 2, 2025, [https://dev.to/sreeni5018/simplify-ai-agent-development-with-pydanticai-a-game-changer-for-python-developers-3moo](https://dev.to/sreeni5018/simplify-ai-agent-development-with-pydanticai-a-game-changer-for-python-developers-3moo)  
16. Pydantic, accessed April 2, 2025, [https://pydantic.dev/](https://pydantic.dev/)  
17. How to Create Routes with FastAPI | by Joël-Steve N. | Medium, accessed April 2, 2025, [https://jnikenoueba.medium.com/how-to-create-routes-with-fastapi-42742f9d2cc1](https://jnikenoueba.medium.com/how-to-create-routes-with-fastapi-42742f9d2cc1)  
18. Request Body \- FastAPI, accessed April 2, 2025, [https://fastapi.tiangolo.com/tutorial/body/](https://fastapi.tiangolo.com/tutorial/body/)  
19. Fast API Background Tasks: Leveraging Pydantic Models for Structured Data \- Orchestra, accessed April 2, 2025, [https://www.getorchestra.io/guides/fast-api-background-tasks-leveraging-pydantic-models-for-structured-data](https://www.getorchestra.io/guides/fast-api-background-tasks-leveraging-pydantic-models-for-structured-data)  
20. Optimizing FastAPI for Concurrent Users when Running Hugging Face ML Models, accessed April 2, 2025, [https://www.youtube.com/watch?v=ARNYcHRrdmY](https://www.youtube.com/watch?v=ARNYcHRrdmY)  
21. MR-GREEN1337/awesome-mcp-fastapi \- GitHub, accessed April 2, 2025, [https://github.com/MR-GREEN1337/awesome-mcp-fastapi](https://github.com/MR-GREEN1337/awesome-mcp-fastapi)  
22. PydanticAI for Building Agentic AI-Based LLM Applications \- areca data, accessed April 2, 2025, [https://www.arecadata.com/pydanticai-for-building-agentic-ai-based-llm-applications/](https://www.arecadata.com/pydanticai-for-building-agentic-ai-based-llm-applications/)  
23. Building Intelligent AI Agents with PydanticAI and RAG: A Step-by-Step Guide \- Medium, accessed April 2, 2025, [https://medium.com/@eng.aa.azeem/building-intelligent-ai-agents-with-pydanticai-and-rag-a-step-by-step-guide-9248bf47ac0b](https://medium.com/@eng.aa.azeem/building-intelligent-ai-agents-with-pydanticai-and-rag-a-step-by-step-guide-9248bf47ac0b)  
24. 10 Essential Things to Know About PydanticAI for Building Reliable AI-Powered Applications | by allglenn \- Stackademic, accessed April 2, 2025, [https://blog.stackademic.com/10-essential-things-to-know-about-pydanticai-for-building-reliable-ai-powered-applications-34c36379c9db](https://blog.stackademic.com/10-essential-things-to-know-about-pydanticai-for-building-reliable-ai-powered-applications-34c36379c9db)  
25. Choosing the right agentic AI framework: SmolAgents, PydanticAI, and LlamaIndex AgentWorkflows \- QED42, accessed April 2, 2025, [https://www.qed42.com/insights/choosing-the-right-agentic-ai-framework-smolagents-pydanticai-and-llamaindex-agentworkflows](https://www.qed42.com/insights/choosing-the-right-agentic-ai-framework-smolagents-pydanticai-and-llamaindex-agentworkflows)  
26. Models \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/models/](https://ai.pydantic.dev/models/)  
27. Mastering PydanticAI: Enhancing AI Agents with Function Tools \- Day 3 \- Medium, accessed April 2, 2025, [https://medium.com/@nninad/mastering-pydanticai-enhancing-ai-agents-with-function-tools-day-3-39139713cb1c](https://medium.com/@nninad/mastering-pydanticai-enhancing-ai-agents-with-function-tools-day-3-39139713cb1c)  
28. Function Tools \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/tools/](https://ai.pydantic.dev/tools/)  
29. A Fun PydanticAI Example For Automating Your Life \- Christopher Samiullah, accessed April 2, 2025, [https://christophergs.com/blog/pydantic-ai-example-github-actions](https://christophergs.com/blog/pydantic-ai-example-github-actions)  
30. pydantic\_ai.models.function \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/api/models/function/](https://ai.pydantic.dev/api/models/function/)  
31. Building a Simple AI Agent with PydanticAI: A Basic Agent Tool Call Example | by Lalit, accessed April 2, 2025, [https://lalitgehani.medium.com/building-a-simple-ai-agent-with-pydanticai-a-basic-agent-tool-call-example-506a72ab1646](https://lalitgehani.medium.com/building-a-simple-ai-agent-with-pydanticai-a-basic-agent-tool-call-example-506a72ab1646)  
32. Agents \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/agents/](https://ai.pydantic.dev/agents/)  
33. Create AI Agent CRUD Application with PydanticAI: Step by Step | by Skolo Online Learning, accessed April 2, 2025, [https://skolo-online.medium.com/create-ai-agent-crud-application-with-pydanticai-step-by-step-524f36aba381](https://skolo-online.medium.com/create-ai-agent-crud-application-with-pydanticai-step-by-step-524f36aba381)  
34. Connecting AI Agents to the World: FastAPI \+ PydanticAI Guide \- YouTube, accessed April 2, 2025, [https://www.youtube.com/watch?v=6yebvAqbFvI](https://www.youtube.com/watch?v=6yebvAqbFvI)  
35. Server \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/mcp/server/](https://ai.pydantic.dev/mcp/server/)  
36. How to create an actual backend api, which uses PydanticAi agents? · Issue \#783 \- GitHub, accessed April 2, 2025, [https://github.com/pydantic/pydantic-ai/issues/783](https://github.com/pydantic/pydantic-ai/issues/783)  
37. Chat App with FastAPI \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/examples/chat-app/](https://ai.pydantic.dev/examples/chat-app/)  
38. Exploring Pydantic and PydanticAI | by DhanushKumar \- Medium, accessed April 2, 2025, [https://medium.com/@danushidk507/exploring-pydantic-and-pydanticai-6d582d285443](https://medium.com/@danushidk507/exploring-pydantic-and-pydanticai-6d582d285443)  
39. Client \- PydanticAI, accessed April 2, 2025, [https://ai.pydantic.dev/mcp/client/](https://ai.pydantic.dev/mcp/client/)