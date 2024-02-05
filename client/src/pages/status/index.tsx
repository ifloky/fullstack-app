import { Button, Result, Row } from "antd";
import { Link, useParams } from "react-router-dom"

const Statuses: Record<string, string> = {
  created: "Employee successfully created",
  updated: "Employee successfully updated",
  deleted: "Employee successfully deleted",
}

export const Status = () => {
  const { status } = useParams();

  return (
    <Row align="middle" justify="center" style={{ width: '100%' }}>
      <Result
        status={status ? 'success' : 404}
        title={status ? Statuses[status] : 'not founded'}
        extra={
          <Button key='dashboard'>
            <Link to='/'>
              On main page
            </Link>
          </Button>
        }
      />
    </Row>
  )
} 
